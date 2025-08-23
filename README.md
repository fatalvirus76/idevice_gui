# iDevice Toolbox GUI

A modern, cross-platform graphical user interface for the powerful **libimobiledevice** command-line tool suite.  
This application provides a user-friendly, tabbed interface to interact with iOS devices, eliminating the need to memorize dozens of complex commands and arguments for tools like `idevicerestore`, `idevicebackup2`, and `irecovery`.


## ✨ Features

This application is a comprehensive toolkit for managing iOS devices, providing a vast array of features organized by the underlying command-line tool.

### General Application Features
- **Modern Interface:** A clean, intuitive, and restyled UI for a better user experience.  
- **Theming:** Multiple themes (Light, Dark, Dracula, Matrix, Synthwave).  
- **Multi-Language Support:** Switch between English and Swedish on the fly.  
- **Persistent Settings:** Remembers window size, position, theme, and language.  
- **Drag & Drop:** Easily drag files (like `.ipsw` firmware) to the correct input fields.  
- **Live Command Preview:** See the exact command before running it.  
- **Integrated Terminal:** Real-time, color-coded CLI output inside the app.  
- **Device Detection:** Automatically detects connected devices by UDID.  

### Integrated Tool Support
The GUI provides a dedicated tab with a full set of controls for nearly every tool in the **libimobiledevice** suite:

- `ideviceinfo` – Get detailed device information (domains, keys).  
- `idevicediagnostics` – Access diagnostics, restart, shutdown, sleep.  
- `idevicebackup2` – Create/restore backups, manage encryption, iCloud.  
- `ideviceprovision` – Manage provisioning profiles.  
- `idevicerestore` – Restore iOS using `.ipsw` files with advanced options.  
- `ideviceimagemounter` – Mount developer disk images.  
- `idevicecrashreport` – Fetch and save crash reports.  
- `idevicesyslog` – Stream system logs in real-time with filters.  
- `idevicepair` – Manage device pairings.  
- `ideviceactivation` – Manage activation state.  
- `idevicedebug` – Run and debug apps.  
- `idevicename` – View or change device name.  
- `idevicedate` – Get, set, or sync date/time.  
- `idevicescreenshot` – Take screenshots.  
- `idevicesetlocation` – Spoof GPS location.  
- `idevicenotificationproxy` – Post/observe notifications.  
- `idevice_id` – List connected devices by UDID.  
- `idevicedebugserverproxy` – Proxy a debug server connection.  
- `irecovery` – Low-level DFU/Recovery interface (send commands, files, scripts).  

---

## 📦 Dependencies

### Python
- [PyQt5](https://pypi.org/project/PyQt5/)  
  Install via pip:  
  ```bash
  pip install PyQt5
