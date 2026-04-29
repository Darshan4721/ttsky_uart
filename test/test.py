import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

@cocotb.test()
async def test_uart_serial(dut):
    dut._log.info("Start Serial UART Test")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    # Wait for reset to be applied
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    # Give the UART a few cycles to initialize
    await ClockCycles(dut.clk, 10)

    # Helper function to shift in 16 bits (e.g., prescale)
    async def shift_in_16(val):
        for i in range(16):
            bit = (val >> i) & 1
            # ui_in[1] = sin, ui_in[2] = shift_en, rxd must be 1 (idle)
            dut.ui_in.value = (bit << 1) | (1 << 2) | (1 << 0)
            await ClockCycles(dut.clk, 1)
        # Clear shift_en, keeping rxd=1
        dut.ui_in.value = (1 << 0)
        await ClockCycles(dut.clk, 1)

    # Set prescale
    # We'll use a very small prescale to make the simulation fast!
    # For a 10us clock (100KHz), prescale=2 means baud=100KHz/(2*8) = 6250 baud
    # prescale << 3 = 16 cycles per bit
    dut._log.info("Setting prescale to 2")
    await shift_in_16(2)
    # Pulse load_prescale (ui_in[3])
    dut.ui_in.value = (1 << 3) | (1 << 0)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = (1 << 0)
    await ClockCycles(dut.clk, 1)

    # Test 1: TX
    # We want to send the character 0xA5
    test_char = 0xA5
    dut._log.info(f"Test 1: TX character 0x{test_char:02X}")
    # We only need to shift the bottom 8 bits into the SIPO, so we shift 8 times
    for i in range(8):
        bit = (test_char >> i) & 1
        dut.ui_in.value = (bit << 1) | (1 << 2) | (1 << 0)
        await ClockCycles(dut.clk, 1)
    dut.ui_in.value = (1 << 0)
    await ClockCycles(dut.clk, 1)

    # Assert s_axis_tvalid (ui_in[4])
    dut.ui_in.value = (1 << 4) | (1 << 0)
    
    # Wait for s_axis_tready to go high and low
    # s_axis_tready is uo_out[2]
    await Timer(1, units="ns")
    while not (int(dut.uo_out.value) & (1 << 2)):
        await ClockCycles(dut.clk, 1)
        await Timer(1, units="ns")
    
    # It was accepted, clear tvalid
    dut.ui_in.value = (1 << 0)

    # Now monitor the TX pin (uo_out[0]) to see the UART waveform!
    dut._log.info("Waiting for start bit on TX...")
    while (int(dut.uo_out.value) & 1) == 1:
        await ClockCycles(dut.clk, 1)
        await Timer(1, units="ns")
    
    dut._log.info("Start bit detected! Waiting for TX to complete...")
    
    # Wait for tx_busy (uo_out[4]) to go low
    await Timer(1, units="ns")
    while (int(dut.uo_out.value) & (1 << 4)):
        await ClockCycles(dut.clk, 1)
        await Timer(1, units="ns")
        
    dut._log.info("TX completed.")

    # Test 2: RX
    test_rx_char = 0x3C
    dut._log.info(f"Test 2: RX character 0x{test_rx_char:02X}")
    
    # We simulate an RX waveform into rxd (ui_in[0])
    # Bit time is prescale * 8 = 16 clock cycles
    BIT_CYCLES = 16
    
    # Start bit (0)
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, BIT_CYCLES)
    
    # Data bits (LSB first)
    for i in range(8):
        bit = (test_rx_char >> i) & 1
        dut.ui_in.value = (bit << 0)
        await ClockCycles(dut.clk, BIT_CYCLES)
        
    # Stop bit (1)
    dut.ui_in.value = (1 << 0)
    await ClockCycles(dut.clk, BIT_CYCLES)

    # Wait for m_axis_tvalid (uo_out[3]) to go high
    await Timer(1, units="ns")
    while not (int(dut.uo_out.value) & (1 << 3)):
        await ClockCycles(dut.clk, 1)
        await Timer(1, units="ns")
        
    dut._log.info("RX character received by UART.")
    
    # Pulse load_piso (ui_in[6]) and m_axis_tready (ui_in[5])
    # to capture it into PISO and acknowledge the stream
    dut.ui_in.value = (1 << 6) | (1 << 5) | (1 << 0)
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = (1 << 0)
    await ClockCycles(dut.clk, 1)
    
    # Shift out the PISO
    rx_val = 0
    for i in range(8):
        await Timer(1, units="ns")
        # sout is uo_out[1]
        bit = (int(dut.uo_out.value) >> 1) & 1
        rx_val |= (bit << i)
        # assert shift_en
        dut.ui_in.value = (1 << 2) | (1 << 0)
        await ClockCycles(dut.clk, 1)
        
    dut.ui_in.value = (1 << 0)
    await ClockCycles(dut.clk, 1)
    
    dut._log.info(f"Received from PISO: 0x{rx_val:02X}")
    
    assert rx_val == test_rx_char, f"Expected 0x{test_rx_char:02X}, got 0x{rx_val:02X}"
    dut._log.info("Test passed!")
