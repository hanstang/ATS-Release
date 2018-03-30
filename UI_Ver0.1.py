import tkinter as Tkinter
import tkinter.messagebox as tkm
import time
import threading
import serial
import datetime

class operationTask(threading.Thread):
	operation_status="stop" #"run" and "stop"
	def __init__(self, listCmd, serial):
		threading.Thread.__init__(self)
		self.command_list = listCmd
		self.ser = serial
		
	def run(self):
		counter_loop=1
		while self.operation_status=="run":
			print("Cycle : " + str(counter_loop))
			print("Time  : " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			print("===================================================")
			
			for command in self.command_list:
				if self.operation_status=="stop":
					print("=====Stop=======")
					break
				if command.isdigit():
					print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : Waiting for "+command+" Second(s)")
					time.sleep(int(command))
				else:	
					self.ser.write(command.encode('utf-8'))
					print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +self.readCommandCode(command))
					time.sleep(int(1))
			
			print("===================================================")
			counter_loop+=1
			
	def readCommandCode(self,cmd):
		if cmd=="u":
			return "Up Button pushed"
		if cmd=="d":
			return "Down button pushed"
		if cmd=="l":
			return "Left Button pushed"
		if cmd=="r":
			return "Right button pushed"
		if cmd=="o":
			return "OK button pushed"
		if cmd=="p":
			return "Power button pushed"
		if cmd=="m":
			return "Menu button pushed"
		if cmd=="h":
			return "Home button pushed"
		if cmd=="n":
			return "Turn AC ON"
		if cmd=="f":
			return "Turn AC OFF"
			
		return "Unknown Code"
	
class GuiPart:
	ctr_command=1
	command_list=[]
	ser = serial.Serial("COM5", 9600, timeout=2) # Establish the connection on a specific port
	operationTask = ""
	
	def __init__(self, parent):
		self.window = parent
		##########################################Remote Control####################################
		self.frame_remote = Tkinter.Frame(window)
		self.lab_remote = Tkinter.Label(self.frame_remote, text ="Remote Control").grid(row=0,column=0)
        
		self.btn_up = Tkinter.Button(self.frame_remote, text ="up", width=10, command=self.btnUP)
		self.btn_up.grid(row=1,column=1,padx=5,pady=5)
        
		self.btn_down = Tkinter.Button(self.frame_remote, text = "down", width=10, command=self.btnDown)
		self.btn_down.grid(row=3,column=1,padx=5,pady=5)
        
		self.btn_left = Tkinter.Button(self.frame_remote, text ="left", width=10, command=self.btnLeft)
		self.btn_left.grid(row=2,column=0,padx=5,pady=5)
        
		self.btn_right = Tkinter.Button(self.frame_remote, text ="right", width=10, command=self.btnRight)
		self.btn_right.grid(row=2,column=2,padx=5,pady=5)
        
		self.btn_ok = Tkinter.Button(self.frame_remote, text ="OK", width=10, command=self.btnOK)
		self.btn_ok.grid(row=2,column=1,padx=5,pady=5)
        
		self.btn_power = Tkinter.Button(self.frame_remote, text ="power", width=10, command=self.btnPower)
		self.btn_power.grid(row=1,column=3,padx=5,pady=5)
       
		self.btn_menu = Tkinter.Button(self.frame_remote, text ="menu", width=10,command=self.btnMenu)
		self.btn_menu.grid(row=2,column=3,padx=5,pady=5)
       
		self.btn_home = Tkinter.Button(self.frame_remote, text = "home", width=10,command=self.btnHome)
		self.btn_home.grid(row=3,column=3,padx=5, pady=5)
		############################################################################################

		##########################################AC################################################
		self.frame_AC = Tkinter.Frame(window)
		self.lab_AC = Tkinter.Label(self.frame_AC, text ="AC").grid(row=0,column=0)

		self.btn_AC_on = Tkinter.Button(self.frame_AC, text ="on", width=10, command=self.btnACon)
		self.btn_AC_on.grid(row=1,column=0,padx=5,pady=5)

		self.btn_AC_off = Tkinter.Button(self.frame_AC, text ="off", width=10, command=self.btnACoff)
		self.btn_AC_off.grid(row=1,column=1,padx=5,pady=5)
		############################################################################################

		#########################################Command############################################
		self.frame_command = Tkinter.Frame(window)
		self.lab_command = Tkinter.Label(self.frame_command, text ="Command").grid(row=0,column=0)

		self.listbox_command = Tkinter.Listbox(self.frame_command, width=30)
		self.listbox_command.grid(row=1,column=0,padx=5,pady=5, columnspan=2)

		self.btn_run = Tkinter.Button(self.frame_command, text ="run", width=10, command=self.btnRun)
		self.btn_run.grid(row=2,column=0,padx=5,pady=5)

		self.btn_stop = Tkinter.Button(self.frame_command, text ="stop", width=10, command=self.btnStop)
		self.btn_stop.grid(row=2,column=1,padx=5,pady=5)

		self.btn_clear = Tkinter.Button(self.frame_command, text ="clear", width=10, command=self.btnClear)
		self.btn_clear.grid(row=3,column=0,padx=5,pady=5)

		self.btn_stop.config(state="disabled") #disabled and normal
		############################################################################################
		
		
		#######################################LOG##################################################
		self.frame_log = Tkinter.Frame(window)
		self.lab_log= Tkinter.Label(self.frame_log, text ="Log").grid(row=0,column=0)
		
		############################################################################################

		#########################################Delay##############################################
		self.frame_delay = Tkinter.Frame(window)
		self.lab_delay = Tkinter.Label(self.frame_delay, text ="Delay").grid(row=0,column=0)
        
		self.sbox_delay = Tkinter.Spinbox(self.frame_delay, width=10, from_=0, to=100000)
		self.sbox_delay.grid(row=1,column=0,padx=5,pady=5)
		self.lab_second = Tkinter.Label(self.frame_delay, text ="Second(s)").grid(row=1,column=1)
		self.btn_submit = Tkinter.Button(self.frame_delay, text ="Submit", width=10, command=self.btnSubmit).grid(row=1,column=2,padx=5,pady=5)
		############################################################################################

		##########################################Grid##############################################
		self.frame_remote.grid(row=0,column=0, sticky="wn")
		self.frame_delay.grid(row=1,column=0,sticky="wn")
		self.frame_AC.grid(row=2,column=0, sticky="wn")
		self.frame_command.grid(row=0,column=1, sticky="wn", rowspan=2)
		#self.frame_log.grid(row=3,column=0,sticky="wn", columnspan=2)
		############################################################################################

		self.ConnectArduinoSerial(self.ser)


	#########################################Serial Function###########################################
	def ConnectArduinoSerial(self,ser):
		print("Connecting to Arduino.....")
		for i in range (1,10):
			rv=ser.readline()
			print("Loading...")
			#Debug print (rv) # Read the newest output from the Arduino
			print (rv.decode("utf-8")) #doesn't show anything ???
			ser.flushInput()
			time.sleep(1) # Delay for one tenth of a secon
			Str=rv.decode("utf-8")
			#Debug print(Str[0:5])
			if Str[0:5]=="Ready":  
				  print("Get Arduino Ready !")
				  break
		
	###################################################################################################

	#########################################BUTTON FUNCTION###########################################
	def btnUP(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push UP Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("u")
		
	def btnDown(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Down Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("d")
		
	def btnLeft(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Left Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("l")
		
	def btnRight(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Right Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("r")
		
	def btnOK(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push OK Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("o")
		
	def btnPower(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Power Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("p")

	def btnMenu(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Menu Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("m")
		
	def btnHome(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Home Button")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("h")

	def btnSubmit(self):
		delayTime=self.sbox_delay.get()
		if delayTime.isdigit():
			if int(delayTime) > 0:
				#add to listbox_command
				self.listbox_command.insert(self.ctr_command,"Delay for " + delayTime + " Second(s)")
				self.ctr_command+=1
				#add command to variable
				self.command_list.append(delayTime)
			else:
				tkm.showerror("Error", "Please Input Number Greater Than 0")
		else:
			tkm.showerror("Error", "Please Input Positive Number")

	def btnACon(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Turn AC On")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("n")
		
	def btnACoff(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Turn AC Off")
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("f")
			
	def btnClear(self):
		#clear listbox_command
		self.listbox_command.delete(0, self.ctr_command)
		#reset variable ctr_command
		self.ctr_command=1
		#clear variable
		self.command_list.clear()
		
	def btnStop(self):
		#Stop Operation
		self.operationTask.operation_status="stop"
		#terminate operation
		
		#Change UI
		self.STOP_UI()
		
	def btnRun(self):
		#operation_thread.run()
		global ctr_command
		if self.ctr_command > 1:
			#Change UI
			self.RUN_UI()
			#Run Operation
			self.operationTask=operationTask(self.command_list,self.ser)
			self.operationTask.operation_status="run"
			self.operationTask.start()
		else:
			tkm.showerror("Error", "No Command Setup")	
			
	############################################################################################

	############################################UI FUNCTION#####################################
	def RUN_UI(self):
		######################disabled all button######################
		#disable Frame Remote
		for child in self.frame_remote.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='disable')
		#disable Frame AC
		for child in self.frame_AC.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='disable')
		#disable Frame Delay
		for child in self.frame_delay.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='disable')
		#disable Frame Command
		for child in self.frame_command.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='disable')
		##############################################################
		#enable button which necessary
		self.btn_stop.config(state="normal")	
		
	def STOP_UI(self):
		######################enabled all button######################
		#disable Frame Remote
		for child in self.frame_remote.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		#disable Frame AC
		for child in self.frame_AC.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		#disable Frame Delay
		for child in self.frame_delay.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		#disable Frame Command
		for child in self.frame_command.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		##############################################################
		#disable button which necessary
		self.btn_stop.config(state="disable")	
	############################################################################################


		
window = Tkinter.Tk()
window.title("Tranzas STB Automation Test Ver 0.1")
main_ui=GuiPart(window)
window.mainloop()