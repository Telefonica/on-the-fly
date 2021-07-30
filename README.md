![Supported Python versions](https://img.shields.io/badge/python-3.6-blue.svg?style=flat-square)
![License](https://img.shields.io/badge/license-GNU-green.svg?style=flat-square)

# **on-the-fly**

```
 ▒█████   ███▄    █     ▄▄▄█████▓  ██░ ██  ▓█████       █████  ██▓   ▓██   ██▓
▒██▒  ██▒ ██ ▀█   █     ▓  ██▒ ▓▒▒▓██░ ██  ▓█   ▀     ▓██     ▓██▒    ▒██  ██▒
▒██░  ██▒▓██  ▀█ ██▒    ▒ ▓██░ ▒░░▒██▀▀██  ▒███       ▒████   ▒██░     ▒██ ██░
▒██   ██░▓██▒  ▐▌██▒    ░ ▓██▓ ░  ░▓█ ░██  ▒▓█  ▄     ░▓█▒    ▒██░     ░ ▐██▓░
░ ████▓▒░▒██░   ▓██░      ▒██▒ ░  ░▓█▒░██▓▒░▒████    ▒░▒█░   ▒░██████  ░ ██▒▓░
░ ▒░▒░▒░ ░ ▒░   ▒ ▒       ▒ ░░     ▒ ░░▒░▒░░░ ▒░     ░ ▒ ░   ░░ ▒░▓     ██▒▒▒ 
  ░ ▒ ▒░ ░ ░░   ░ ▒░        ░      ▒ ░▒░ ░░ ░ ░      ░ ░     ░░ ░ ▒   ▓██ ░▒░ 
░ ░ ░ ▒     ░   ░ ░       ░ ░      ░  ░░ ░    ░        ░ ░      ░ ░   ▒ ▒ ░░  
    ░ ░           ░                ░  ░  ░░   ░      ░       ░    ░   ░ ░     

```

Different technologies and paradigms are hyperconnected and offer advances to society. The usage of other technologies among these devices makes security uneven. When facing a pentest in any environment, one major factor is the network. The network interconnects the world of the Internet of Things, the world of industrial control systems, and information technology. This README introduces the 'on-the-fly' tool, which gives capabilities to perform pentesting tests in several domains (IoT, ICS & IT). It is an innovative tool by bringing together different worlds sharing a common factor: the network. 

# Prerequisities
'on-the-fly' was written in Python and made extensive use of Scapy and netfilterqueue. It is crucial to have Scapy in Python and netfilterqueue installed with a compatible version of Python. For this, a version of Python 3 up to Python version 3.7.5 is recommended (and no higher, as there may be incompatibilities with 3.8 and 3.9 in some libraries that it uses 'on-the-fly'). 
There is a requirements.txt file that must be executed the first time the tool is launched using 'pip install -r requirements.txt'. Again the pip version must be oriented to a Python 3 version up to 3.7.5.
```[python]
pip install -r requirements.txt
```

# Usage

```[python]
python on-the-fly.py
```

# Example videos

### *on-the-fly: MySQL_manipulation Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/1kPE-u9YV2Y/0.jpg)](https://www.youtube.com/watch?v=1kPE-u9YV2Y)
### *on-the-fly: SSDP_fake Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/kWb7FWmhyao/0.jpg)](https://youtu.be/kWb7FWmhyao)
### *on-the-fly: Proxy_socks4 Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/YGkGZfPhGk8/0.jpg)](https://www.youtube.com/watch?v=YGkGZfPhGk8)
### *on-the-fly: Port_forwarding Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/t74riJAYfuo/0.jpg)](https://www.youtube.com/watch?v=t74riJAYfuo)
### *on-the-fly: Modbus_spoofing Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/vS5obvdlwHI/0.jpg)](https://www.youtube.com/watch?v=vS5obvdlwHI)
### *on-the-fly: Modbus_sniffing_traffic Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/pnFKwHrdyPU/0.jpg)](https://www.youtube.com/watch?v=pnFKwHrdyPU)
### *on-the-fly: MDNS_Scan Module*
[![on-the-fly: Module ssdp_fake](https://img.youtube.com/vi/o6sOo8-Wqy8/0.jpg)](https://www.youtube.com/watch?v=o6sOo8-Wqy8)


# License

This project is licensed under the GNU General Public License - see the LICENSE file for details
Attributions to third-party software can be found in the licenses_attributions.txt file. These may be contained in portions of code.

# Contact

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. WHENEVER YOU MAKE A CONTRIBUTION TO A REPOSITORY CONTAINING NOTICE OF A LICENSE, YOU LICENSE YOUR CONTRIBUTION UNDER THE SAME TERMS, AND YOU AGREE THAT YOU HAVE THE RIGHT TO LICENSE YOUR CONTRIBUTION UNDER THOSE TERMS. IF YOU HAVE A SEPARATE AGREEMENT TO LICENSE YOUR CONTRIBUTIONS UNDER DIFFERENT TERMS, SUCH AS A CONTRIBUTOR LICENSE AGREEMENT, THAT AGREEMENT WILL SUPERSEDE.

This software doesn't have a QA Process. This software is a Proof of Concept.

If you have any problems, you can contact:

ideaslocas@telefonica.com

