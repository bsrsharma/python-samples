PCI_CLASS_DEVICE = 0x0a      # Device class
PCI_PRIMARY_BUS = 0x18       # Primary bus number
PCI_SECONDARY_BUS = 0x19     # Secondary bus number
PCI_SUBORDINATE_BUS = 0x1a   # Highest bus number behind the bridge
PCI_CLASS_BRIDGE_PCI = 0x0604
PCI_CLASS_PROGRAMMING_INTERFACE = 0x00
#
PORT_PCI_CMD = 0x0cf8
PCI_VENDOR_ID = 0x8086       # default for root port and endpoint
PCI_DEVICE_ID = 0x1450       # default for root port
PCI_CLASS_REVISION = 0x08    # High 24 bits are class, low 8 revision
PCI_HEADER_TYPE = 0x0e       # 8 bits
PCI_HEADER_TYPE_BRIDGE = 1
PCI_HEADER_TYPE_CARDBUS = 2
#
#
RamSize = 0x10000000
MaxPCIBus = 1
# PCIDevice has:
#   Index, Data
#   0      bdf     
#   1      rootbus
#   2      index to next node
#   3      index to previous node
#   4      parent 
#   5      vendor
#   6      device
#   7      PCI_Class
#   8      prog_if
#   9      revision
#   10     header_type
#   11     secondary_bus
#   12     have_driver
#
# bdf = PCI Bus:Device.Function
PCIDevice = []
#
# PCIDevices[] is a linked list of PCIDevice[]; PCIDevice[2] points to next node. A value of -1 indicates no next node. i.e. the last node of a list.
# PCIDevice[3] points to previous node. A value of -1 indicates no previous node. i.e. the first node of a list.
PCIDevices = []
# hlist_head is the index to the first node of PCIDevices[] linked list
hlist_head = 0
#
pci_platform_tbl = []
MaxBDF = 1
currentBDF = 0
BDFList = [0x0080]
PCIDeviceCount = 0
#                       
import struct
#
#
#****************************************************************
# Bus initialization
#****************************************************************
#
# For testing, allow only one Bridge
PCI_BRIDGE_COUNT = 2  # because we call this in pci_bios_init_bus_rec twice
def pci_config_readw(bdf, arg):
  global PCI_BRIDGE_COUNT
  PCI_class = 0
  
  if arg == PCI_CLASS_DEVICE:
    PCI_class = 0
#    print("PCI_BRIDGE_COUNT = ", PCI_BRIDGE_COUNT)
    if PCI_BRIDGE_COUNT > 0:
      PCI_class = PCI_CLASS_BRIDGE_PCI
      PCI_BRIDGE_COUNT = PCI_BRIDGE_COUNT - 1
    else:
      PCI_class = 0  
    return PCI_class
  
def pci_config_readb(bdf, arg):
  if arg == PCI_PRIMARY_BUS:
    return 0
  if arg == PCI_SECONDARY_BUS:
    return 1
  if arg == PCI_SUBORDINATE_BUS:
    return 2
  if arg == PCI_HEADER_TYPE:
    return PCI_HEADER_TYPE
  
  return -1

def pci_config_readl(bdf, arg):
  if arg == PCI_VENDOR_ID:
    return (PCI_DEVICE_ID << 16) | PCI_VENDOR_ID
    
  if arg == PCI_CLASS_REVISION:
    return (PCI_CLASS_BRIDGE_PCI << 16) | (PCI_CLASS_PROGRAMMING_INTERFACE << 8) | (PCI_CLASS_REVISION)
    
  if arg == RES_RESERVE_BUS_RES:
    return RES_RESERVE_BUS_RES
    
  return 0
  
def pci_config_writeb(bdf, arg, n):
  if arg == PCI_PRIMARY_BUS:
    return 0
  if arg == PCI_SECONDARY_BUS:
    return 0
  if arg == PCI_SUBORDINATE_BUS:
    return 0
    
  return -1  
    
    

def pci_find_resource_reserve_capability(bdf):

  return 0;
  
def pci_next(bus):
#  generate the next bdf for this bus; return -1 when there is no more
  global currentBDF
   
  currentBDF = currentBDF + 1
  if currentBDF > MaxBDF:
    return -1
  return BDFList[currentBDF - 1]     
  
def pci_bios_init_bus_rec(bus, pci_bus):
  global currentBDF
  global PCI_BRIDGE_COUNT
#
   
  bdf = 0
  PCI_class = 0
  secbus = 0
  resbus = 0
  cap = 0
  tmp_res_bus = 0
  
#  print('bus = ', bus)
  
# prevent accidental access to unintended devices
  bdf = pci_next(bus)
  while bdf >= 0:
#    print("bdf = ", hex(bdf))
    PCI_class = pci_config_readw(bdf, PCI_CLASS_DEVICE)
    if PCI_class == PCI_CLASS_BRIDGE_PCI:
      pci_config_writeb(bdf, PCI_SECONDARY_BUS, 255)
      pci_config_writeb(bdf, PCI_SUBORDINATE_BUS, 0)
    bdf = pci_next(bus)
#
# Reset currentBDF, PCI_BRIDGE_COUNT so that we restart the scan
  currentBDF = 0
  bdf = pci_next(bus)
#  print("(scan)bdf = ", hex(bdf))  
  while bdf >= 0:
    PCI_class = pci_config_readw(bdf, PCI_CLASS_DEVICE)
#    print("PCI_class = ", hex(PCI_class));
    bdf = pci_next(bus)
    if (PCI_class != PCI_CLASS_BRIDGE_PCI):
      continue
#
    pribus = pci_config_readb(bdf, PCI_PRIMARY_BUS)
    if pribus != bus:
      print("PCI: primary bus = ", hex(pribus), " -> ", hex(bus))
      pci_config_writeb(bdf, PCI_PRIMARY_BUS, bus)
    else:
      print("PCI: primary bus = ", hex(pribus))
      
    secbus = pci_config_readb(bdf, PCI_SECONDARY_BUS)
    pci_bus[0] = pci_bus[0] + 1
    if pci_bus[0] != secbus:
      print("PCI: secondary bus = ", hex(secbus), " -> ", hex(pci_bus[0]))
      secbus = pci_bus[0]
      pci_config_writeb(bdf, PCI_SECONDARY_BUS, secbus)
    else:
      print("PCI: secondary bus = ", hex(secbus))
    # set to max for access to all subordinate buses.
    #       later set it to accurate value
    subbus = pci_config_readb(bdf, PCI_SUBORDINATE_BUS)
    pci_config_writeb(bdf, PCI_SUBORDINATE_BUS, 255)

# recursively call pci_bios_init_bus_rec
    pci_bios_init_bus_rec(secbus, pci_bus)
    
    if subbus != pci_bus[0]:
      res_bus = pci_bus[0]
      cap = pci_find_resource_reserve_capability(bdf)
      if cap != 0:
        tmp_res_bus = pci_config_readl(bdf, cap + RES_RESERVE_BUS_RES)
        if tmp_res_bus != -1:
          res_bus = tmp_res_bus & 0xFF
          if (res_bus + secbus) < secbus or (res_bus + secbus) < res_bus:
            print("PCI: bus_reserve value", res_bus, "is invalid")
            res_bus = 0
            
          if secbus + res_bus > pci_bus[0]:
            print("PCI: QEMU resource reserve cap: bus = ", res_bus)
            res_bus = secbus + res_bus
            
      print("PCI: subordinate bus = ", hex(subbus), " -> ", hex(res_bus))
      subbus = res_bus
      pci_bus[0] = res_bus
    else:
      print("PCI: subordinate bus = 0x%x", subbus)
    
    pci_config_writeb(bdf, PCI_SUBORDINATE_BUS, subbus)
    bdf = pci_next(bus)
    
  return

def outl(addr, data):

  return
  
def inl(addr):  

  return 0x80000000
  
def pci_probe_host():

  outl(0x80000000, PORT_PCI_CMD)
  if inl(PORT_PCI_CMD) != 0x80000000:
    print("Detected non-PCI system")
    return -1
  return 0 
  
def romfile_loadint(filename, value):

   return 0
  
def pci_bios_init_bus():
  extraroots = romfile_loadint("etc/extra-pci-roots", 0)
  bus = 0
  pci_bus = [0]
  
  # host bus
  pci_bios_init_bus_rec(0, pci_bus)
  
  if extraroots != 0:
    while bus < 0xff:
      bus = bus + 1
      pci_bios_init_bus_rec(bus, pci_bus)

  return

# Find all PCI devices and populate PCIDevices linked list
def pci_probe_devices():
  global MaxPCIBus
  global PCIDeviceCount
  
  bdf = 0x0080
  rootbus = 0
  vendev = 0
  classrev = 0
  header_type = 0
  v = 0
  
  print("PCI probe")
#
# busdevs[256] holds indices to bus devices
  busdevs = []
# initialize busdevs[] array with NULL  
  n = 0
  while n < 256:
    busdevs.append(-1)
    n = n + 1
#    

  extraroots = 0
  bus = -1
  lastbus = 0
  rootbuses = 0
  PCIDeviceCount = 0
  
  while bus < 0xff and (bus < MaxPCIBus or rootbuses < extraroots):
    bus = bus + 1
    if bdf > -1:
      # Create new pci_device struct and add to list
      PCIDeviceCount = PCIDeviceCount + 1
      # Find parent device
      parent = busdevs[bus]
      if parent == -1:
        if bus != lastbus:
          rootbuses = rootbuses + 1
        lastbus = bus
        rootbus = rootbuses
        if bus > MaxPCIBus:      
          MaxPCIBus = bus
      else:
        rootbus = PCIDevices[parent][1]
      # Populate pci_device info
      PCIDevice.append(bdf)
      PCIDevice.append(rootbus)
      PCIDevice.append(-1)    # next node
      PCIDevice.append(-1)    # previous node
      PCIDevice.append(parent)
      vendev = pci_config_readl(bdf, PCI_VENDOR_ID)
      PCIDevice.append(vendev & 0xffff)  #vendor
      PCIDevice.append(vendev >> 16)     #device
      classrev = pci_config_readl(bdf, PCI_CLASS_REVISION)
      PCIDevice.append(classrev >> 16)   #PCI_Class
      PCIDevice.append(classrev >> 8)    #programming interface
      PCIDevice.append(classrev & 0xff)  #revision
      header_type = pci_config_readb(bdf, PCI_HEADER_TYPE)
      PCIDevice.append(header_type & 0x7f) #header_type
      v = header_type & 0x7f
      if v == PCI_HEADER_TYPE_BRIDGE or v == PCI_HEADER_TYPE_CARDBUS:
        secbus = pci_config_readb(bdf, PCI_SECONDARY_BUS)
        PCIDevice.append(secbus)           # secondary_bus
        if secbus > bus and busdevs[secbus] != 0:
          busdevs[secbus] = dev
        if secbus > MaxPCIBus:
          MaxPCIBus = secbus
        
      print("PCI device ", hex(PCIDevice[5]), hex(PCIDevice[6]), hex(PCIDevice[7])) # vendor, device, PCI_Class
    
      PCIDevices.append(PCIDevice)
      # invalidate this bdf
      bdf = -1

  print("Found ", PCIDeviceCount, "PCI devices (max PCI bus is ", MaxPCIBus, ")" )
  
  return
  
def pci_init_device(pci_platform_tbl):

  return  
  
def pci_bios_init_platform():

# for each PCI device
  pci_init_device(pci_platform_tbl)
  
  return
  
def pci_bios_check_devices(busses):

  print("PCI: check devices")
  
  return 0
  
def pci_bios_map_devices(busses):

  return

def pci_bios_init_device(pci):

  bdf = PCIDevices[pci][0]
  vendor = PCIDevices[pci][5]
  device = PCIDevices[pci][6]

  print("PCI: init bdf = ", hex(bdf), "id = ", hex(vendor), " : ", hex(device))
  
  return
  
def pci_bios_init_devices():
  pci = 0
  
# for each PCI device
  while pci < PCIDeviceCount:
    pci_bios_init_device(pci)
    pci = pci + 1
  
  return
 
def pci_enable_default_vga():

  return
  
def pci_setup():
#
  busses = []
#  
  print("pci setup")

  print("=== PCI bus & bridge init ===")

  if pci_probe_host() != 0:
    return
    
  pci_bios_init_bus()
  
  print("=== PCI device probing ===")
  
  pci_probe_devices()
  
  pcimem_start = RamSize
  pci_bios_init_platform()
  
  print("=== PCI new allocation pass #1 ===")
  
  if pci_bios_check_devices(busses) != 0:
    return
    
  print("=== PCI new allocation pass #2 ===")
  
  pci_bios_map_devices(busses)

  pci_bios_init_devices()

  pci_enable_default_vga()

  return
#
pci_setup()