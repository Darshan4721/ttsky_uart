![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# Tiny Tapeout Verilog Project Template

- [Read the documentation for project](docs/info.md)

## What is Tiny Tapeout?

Tiny Tapeout is an educational project that aims to make it easier and cheaper than ever to get your digital and analog designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

## Set up your Verilog project

1. Add your Verilog files to the `src` folder.
2. Edit the [info.yaml](info.yaml) and update information about your project, paying special attention to the `source_files` and `top_module` properties. If you are upgrading an existing Tiny Tapeout project, check out our [online info.yaml migration tool](https://tinytapeout.github.io/tt-yaml-upgrade-tool/).
3. Edit [docs/info.md](docs/info.md) and add a description of your project.
4. Adapt the testbench to your design. See [test/README.md](test/README.md) for more information.

The GitHub action will automatically build the ASIC files using [LibreLane](https://www.zerotoasiccourse.com/terminology/librelane/).

## Enable GitHub actions to build the results page

- [Enabling GitHub Pages](https://tinytapeout.com/faq/#my-github-action-is-failing-on-the-pages-part)

## Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## What next?

- [Submit your design to the next shuttle](https://app.tinytapeout.com/).
- Edit [this README](README.md) and explain your design, how it works, and how to test it.
- Share your project on your social network of choice:
  - LinkedIn [#tinytapeout](https://www.linkedin.com/search/results/content/?keywords=%23tinytapeout) [@TinyTapeout](https://www.linkedin.com/company/100708654/)
  - Mastodon [#tinytapeout](https://chaos.social/tags/tinytapeout) [@matthewvenn](https://chaos.social/@matthewvenn)
  - X (formerly Twitter) [#tinytapeout](https://twitter.com/hashtag/tinytapeout) [@tinytapeout](https://twitter.com/tinytapeout)
  - Bluesky [@tinytapeout.com](https://bsky.app/profile/tinytapeout.com)







UART Tiny Tapeout Implementation Walkthrough
We have successfully integrated your UART core into the Tiny Tapeout template by using a serial interface to respect the 8-input/8-output constraint, keeping the uart_ file prefix convention as requested.

Architecture Highlights
NOTE

The Tiny Tapeout standard provides exactly 8 ui_in (dedicated inputs), 8 uo_out (dedicated outputs), and 8 uio (bidirectional IOs). Since the UART module combined with its AXI stream interface has a large number of pins, we designed a serial wrapper.

Top Module Wrapper (uart_top.sv):

Replaced project.sv with uart_top.sv and set the module name to tt_um_uart_serial.
Built a 16-bit SIPO (Serial-In Parallel-Out) register to handle bringing in parallel data serially.
Built an 8-bit PISO (Parallel-In Serial-Out) register to export received data serially.
Connected your untouched uart.v, uart_tx.v, and uart_rx.v to these registers.
Pin Mapping (8 inputs, 8 outputs):

ui_in[0] (rxd): Direct connection to UART RX.
ui_in[1] (sin): Serial data input for the SIPO.
ui_in[2] (shift_en): Controls the shifting of SIPO and PISO.
ui_in[3] (load_prescale): Triggers loading the 16-bit SIPO content into the UART's prescale register.
ui_in[4] (s_axis_tvalid): AXI valid signal to begin UART transmission.
ui_in[5] (m_axis_tready): AXI ready signal to acknowledge received UART data.
ui_in[6] (load_piso): Triggers capturing m_axis_tdata into the PISO.
uo_out[0] (txd): Direct connection to UART TX.
uo_out[1] (sout): Serial data output from the PISO.
uo_out[2:7]: Mapped directly to your UART/AXI status flags (s_axis_tready, m_axis_tvalid, tx_busy, rx_busy, rx_overrun_error, rx_frame_error).
Python Testbench (test.py):

We completely redesigned test.py to be a Cocotb test that operates this serial interface.
Initialization: It shifts 16 bits into the SIPO and pulses load_prescale to set the baud rate.
TX Test: It shifts an 8-bit character (0xA5) into the SIPO, pulses s_axis_tvalid, and monitors the txd pin directly to wait for the UART waveform to complete.
RX Test: It directly drives a simulated UART waveform into the rxd pin, waits for the UART module to assert m_axis_tvalid, captures it into the PISO, and then shifts it out via sout to verify the character (0x3C) was received correctly.
Verification
You can now run your standard Tiny Tapeout build script (make or the GitHub action) to verify the synthesis and simulation. The testbench handles the entire UART TX and RX loop dynamically!





