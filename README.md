# iwlist Parser
The `iwlist` command shows a lot of useful wireless information from nearby
access points in a reasonably concise way and it has become a royal pain to
find any other libraries that show this wireless information succintly or 
that are anything other than skeletons of planned modules from years ago.

This simple parser avoids reinventing the wheel by simply working on top of
a standard linux utility and parsing the output into sensible objects for
use in python.

# Usage

```python
import iwlist_parser

INTERFACE="wlan1"
cells = iwlist_parser.scan(INTERFACE)

if len(cells) > 1:
    print(cell[0].essid,":",cell[0].address)

```

The scan is performed, by default, on the interface "wlan0". The interface is
specified as the first option to scan (as seen above). The interface is simply
a string of the name of the interface:
    
```python
interface  = "wlan0"
interface2 = "wlan2"
interface3 = "ens33"
```

etc.

Note that "ens33" is probably a bad example as it is typically the default
_ethernet_ interface (and this program requires a _wireless_ interface) it
simply illustrates the point that the name of the device doesn't matter so
long as it is a string and a valid wireless device name.

The cells themselves have several fields:

| Field Name | Meaning |
------------------------
| name | The cell name assigned by iwlist (e.g. Cell 01, Cell 02, etc.). This isn't particularly useful other than keeping track |
| channel | The channel on which the AP is operating |
| address | The hardware (MAC) address of the AP |
| frequency | The frequency at which the AP is operating (Should be around 2.4 GHz or 5.0 GHz) |
| quality | The quality of the signal (I actually don't know what this value means) |
| signal_level | The strength of the signal measured in dBm, the higher the value the stronger the signal (e.g. -1 > -20) |
| encryption_key_status | Whether or not an encryption key is used | 
| essid | The ESSID of the AP as reported by `iwlist` |
| bit_rates | A list of the supported bit rates of the AP in Mb/s |
| mode | The mode of the AP |
| group_cipher | The type of group cipher being used (I assume) |
| authentication_suites | Authentication Suite information from the AP |
| extra | Unlabelebed items that I can't figure out the meaning/purpose of |

