# Tiny Tapeout project information
project:
  title:        "Serial UART Wrapper"
  author:       "Antigravity & User"
  discord:      ""
  description:  "UART RX/TX module with a serial (SIPO/PISO) AXI stream wrapper"
  language:     "SystemVerilog"
  clock_hz:     0

  # How many tiles your design occupies? A single tile is about 167x108 uM.
  tiles: "1x1"

  # Your top module name must start with "tt_um_". Make it unique by including your github username:
  top_module:  "tt_um_uart_serial"

  # List your project's source files here.
  source_files:
    - "uart_top.sv"
    - "uart.v"
    - "uart_tx.v"
    - "uart_rx.v"

# The pinout of your project. Leave unused pins blank. DO NOT delete or add any pins.
# This section is for the datasheet/website. Use descriptive names (e.g., RX, TX, MOSI, SCL, SEG_A, etc.).
pinout:
  # Inputs
  ui[0]: "rxd"
  ui[1]: "sin"
  ui[2]: "shift_en"
  ui[3]: "load_prescale"
  ui[4]: "s_axis_tvalid"
  ui[5]: "m_axis_tready"
  ui[6]: "load_piso"
  ui[7]: ""

  # Outputs
  uo[0]: "txd"
  uo[1]: "sout"
  uo[2]: "s_axis_tready"
  uo[3]: "m_axis_tvalid"
  uo[4]: "tx_busy"
  uo[5]: "rx_busy"
  uo[6]: "rx_overrun_error"
  uo[7]: "rx_frame_error"

  # Bidirectional pins
  uio[0]: ""
  uio[1]: ""
  uio[2]: ""
  uio[3]: ""
  uio[4]: ""
  uio[5]: ""
  uio[6]: ""
  uio[7]: ""


# Do not change!
yaml_version: 6
