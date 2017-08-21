import visa
import struct
import binascii

class Keithley2400(object):
    
    def init(self, gpib):
        """Set up gpib controller for device"""
        
        assert(gpib >= 0), "Please enter a valid gpib address"
        self.gpib_addr = gpib
        
        print "Initializing keithley 2400"
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(rm.list_resources()[0])
        for x in rm.list_resources():
            if str(self.gpib_addr) in x:
                print "found"
                self.inst = rm.open_resource(x)
                
        
        print self.inst.query("*IDN?;")
        self.inst.write("*RST;")
        #self.inst.query("*RST;*IDN?;")
        self.inst.write("*ESE 1;*SRE 32;*CLS;:FUNC:CONC ON;:FUNC:ALL;:TRAC:FEED:CONT NEV;:RES:MODE MAN;")
        print self.inst.query(":SYST:ERR?;")
        self.inst.timeout= 10000
        
    
    def get_source_mode(self, x):
        return{
            0:"VOLT",
            1:"CURR"
        }.get(x, "VOLT")
        
    def configure_measurement(self, _funct=0):
        """Set what we are measuring and autoranging"""      
          
        funct = {0:":VOLT", 1:":CURR", 2:":RES"}.get(_funct, ":CURR")
        self.inst.write(funct+":RANG:AUTO ON;")
    
    def configure_source(self, _func, output_level, compliance):
        """Set output level and function"""
        
        assert(source_mode>=0 and source_mode<2), "Invalid Source function"
        assert(output_level>-1100 and output_level < 1100), "Voltage out of range"
        assert(compliance<0.5), "Compliance out of range"
        func = {0:"VOLT", 1:"CURR"}.get(_func, "VOLT")
        self.inst.write("SOUR:FUNC "+func+";:SOUR:"+func+" "+str(float(output_level))+";:CURR:PROT "+str(float(compliance))+";")
        
    def out_source(self, level):
        self.inst.write(":SOUR:VOLT "+str(float(level)))
        self.enable_output(True)
    def enable_output(self, output):
        """Sets output of front panel"""
        
        if output is True:
            self.inst.write("OUTP ON;")
            return
        self.inst.write("OUTP OFF;")
        
    def configure_multipoint(self, arm_count=1, trigger_count=1, mode=0):
        """Configures immediate triggering and arming"""
        
        assert(mode>=0 and mode <3), "Invalid mode"
        source_mode = {0:"FIX", 1:"SWE", 2:"LIST"}.get(mode)
        print str(arm_count)+" "+str(trigger_count)+" "+str(mode)
        self.inst.write(":ARM:COUN "+str(arm_count)+";:TRIG:COUN "+str(trigger_count)+";:SOUR:VOLT:MODE "+source_mode+";:SOUR:CURR:MODE "+source_mode)
        
    def configure_trigger(self):
        self.inst.write("ARM:SOUR IMM;:ARM:TIM 0.010000;:TRIG:SOUR IMM;:TRIG:DEL 0.000000;")
        
    def initiate_trigger(self):
        self.inst.write(":TRIG:CLE;:INIT;")
    
    def wait_operation_complete(self):
        self.inst.write("*OPC;")


    # TODO parse data from visa buffer 
    def fetch_measurements(self):
        read_bytes = self.inst.query(":FETC?")
        print "bytes: "+read_bytes
        return (float(read_bytes.split(",")[0]), float(read_bytes.split(",")[1]))
        
    def read_single_point(self):
        self.configure_multipoint()
        self.configure_trigger()
        self.initiate_trigger()
        self.wait_operation_complete()
        return self.fetch_measurements()
        

    