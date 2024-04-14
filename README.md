# UI for 2023-24 FSO laser sender/receiver capstone project

## List of files
| Path | Description |
|-----------------------------------------------|------------------|
| `updated_sensor_code/updated_sensor_code.ino` | arduino code which gathers data from all sensors and the photodiode and sends it via serial |
| `graph_readings_pyqt6.py`                     | UI program - receives serial data from Arduino and displays it to continuously-updating graphs |
| `communications_testing.py`                   | Partial implementation of the UI which only prints received values to the screen as they come in |
| `requirements.txt`                            | list of required python libraries |

## Notes
- The UI assumes that the arduino is located at `/dev/ttyACM0`. This assumption might be broken if running on windows, if another serial device is connected, or if the arduino is disconnected and re-connected while the program is running
- The UI code could do with some re-factoring. Currently it has separate classes for each set of multiple variables that need to be plotted; it should probably be one class that can handle any number of variables.
- Time from the sensors and time from the photodiode may be different, as time from the photodiode is sent as an offset instead of an absolute value. This allows for the fast transfer time needed to reach around 1 kHz, but means that 0 for the sensors is the start time of the arduino while 0 for the photodiode is the time that the first reading was received by the UI. In addition, spacing between readings may be lost if any photodode readings are skipped due to lack of synchronization between the arduino and the UI (arduino sends values as fast as it can while UI just reads one per second, flushing the buffer first to avoid getting behind).
- There is certainly optimization to be done with the UI - it runs quite slowly, with these being some potential reasons:
  - time spent waiting for serial communication to come in
  - re-drawing graphs every time they update (even if they aren't visible)
- Future work could involve embedding a stream from the raspberry pi camera into the UI - currently it's accessed through a start menu shortcut instead
