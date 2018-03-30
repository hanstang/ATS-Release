import tkinter as Tkinter
import tkinter.messagebox as tkm
import time
import threading
import serial
import datetime
import urllib3
import os
import serial.tools.list_ports
import socket
from tkinter import filedialog, Menu

class operationTask(threading.Thread):
	operation_status="stop" #"run" and "stop"
	def __init__(self, listCmd, serial, yawcamURL, captureDir, cycles):
		threading.Thread.__init__(self)
		self.command_list = listCmd
		self.ser = serial
		self.yawcamURL = yawcamURL.get()
		self.captureDir = captureDir.get()
		self.cycles = cycles
		
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
				if command.isdigit(): #Delay
					print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : Waiting for "+command+" Second(s)")
					time.sleep(int(command))
				elif command=="cap": #capture 
					print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +self.capturingMonitor(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
					time.sleep(int(1))
				else: #arduino command
					self.ser.write(command.encode('utf-8'))
					print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +self.readCommandCode(command))
					time.sleep(int(1))
			
			print("===================================================")
			if (counter_loop >= int(self.cycles)) :
				print("Has been stopped, please push stop button")
				break
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
	
	def capturingMonitor(self,name):
		try:
			http = urllib3.PoolManager()
			r = http.request('GET', self.yawcamURL, preload_content=False, timeout=1)
			
			if not os.path.exists(self.captureDir):
				os.makedirs(self.captureDir)
			
			if r.status==200:
				with open(self.captureDir+"/"+name+'.jpg', 'wb') as out:
					while True:
						data = r.read()
						if not data:
							break
						out.write(data)
				return "Captured " + name + ".jpg Success"
			else:
				return "Capture Failed: Unknown Error"
				
		except urllib3.exceptions.HTTPError:
			return "Capture Failed: Server Not Found"
	
	def printAndLog(self,text,url):
		#print on cmd
		print (text)
		#put on notepad
		f = open(url,"a")
		f.write(text)
		f.close
		
		
class GuiPart:
	ctr_command=1
	command_list=[]
	ser = ""
	operationTask = ""
	
	def __init__(self, parent):
		self.window = parent
		
		##########################################Menu Bar##########################################
		menubar = Menu(window)
		
		fileMenu = Menu(menubar, tearoff=0)
		fileMenu.add_command(label="Save",command=self.btnSaveCommand)
		fileMenu.add_command(label="Open/Load",command=self.btnLoadCommand)
		fileMenu.add_separator()
		fileMenu.add_command(label="Exit", command=window.quit)
		
		menubar.add_cascade(label="File", menu=fileMenu)
		############################################################################################
		
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

		self.listbox_command = Tkinter.Listbox(self.frame_command, width=30, height=10)
		self.listbox_command.grid(row=1,column=0,pady=5, columnspan=2)
		
		self.scrollbar_command = Tkinter.Scrollbar(self.frame_command, command=self.listbox_command.yview)
		self.scrollbar_command.grid(row=1,column=2)
		
		self.listbox_command.configure(yscrollcommand = self.scrollbar_command.set)

		self.btn_run = Tkinter.Button(self.frame_command, text ="run", width=10, command=self.btnRun)
		self.btn_run.grid(row=2,column=0,padx=5,pady=5)

		self.btn_stop = Tkinter.Button(self.frame_command, text ="stop", width=10, command=self.btnStop)
		self.btn_stop.grid(row=2,column=1,padx=5,pady=5)

		self.btn_clear = Tkinter.Button(self.frame_command, text ="clear", width=10, command=self.btnClear)
		self.btn_clear.grid(row=3,column=0,padx=5,pady=5)
		
		self.btn_reset_arduino = Tkinter.Button(self.frame_command, text ="Reset Arduino", width=10, command=self.btnResetArduino)
		self.btn_reset_arduino.grid(row=3,column=1,padx=5,pady=5)
		
		self.lab_cycle = Tkinter.Label(self.frame_command, text ="Cycle : ").grid(row=4,column=0)
		self.sbox_cycle = Tkinter.Spinbox(self.frame_command, width=10, from_=1, to=100000)
		self.sbox_cycle.grid(row=4,column=1,padx=5,pady=5)

		self.btn_stop.config(state="disabled") #disabled and normal
		############################################################################################
		
		
		#######################################LOG##################################################
		self.frame_log = Tkinter.Frame(window)
		self.lab_log= Tkinter.Label(self.frame_log, text ="Log").grid(row=0,column=0)
		############################################################################################

		#########################################Delay##############################################
		self.frame_delay = Tkinter.Frame(window)
		self.lab_delay = Tkinter.Label(self.frame_delay, text ="Delay").grid(row=0,column=0)
        
		self.delayValue = Tkinter.StringVar()
		self.delayValue.set(1)
		
		self.sbox_delay = Tkinter.Spinbox(self.frame_delay, width=10, from_=1, to=100000, textvariable=self.delayValue)
		self.sbox_delay.grid(row=1,column=0,padx=5,pady=5)
		
		self.lab_second = Tkinter.Label(self.frame_delay, text ="Second(s)").grid(row=1,column=1)
		self.btn_submit = Tkinter.Button(self.frame_delay, text ="Submit", width=10, command=self.btnSubmitDelay).grid(row=1,column=2,padx=5,pady=5)
		############################################################################################
		
		##################################Serial Port Setting#######################################
		self.frame_serial = Tkinter.Frame(window)
		self.lab_serial = Tkinter.Label(self.frame_serial, text ="Serial Port Setting").grid(row=0,column=0)
		
		self.ports = list(serial.tools.list_ports.comports())	#get port list
		
		self.serialValue = Tkinter.StringVar()
		self.serialValue.set(self.ports[0])
		
		self.oMenu_serial = Tkinter.OptionMenu(self.frame_serial, self.serialValue, *self.ports)
		self.oMenu_serial.grid(row=1,column=0,padx=5,pady=5)
		
		self.btn_connect = Tkinter.Button(self.frame_serial, text ="Connect", width=10, command=self.btnConnect)
		self.btn_connect.grid(row=1,column=1,padx=5,pady=5)
		############################################################################################
		
		################################Camera######################################################
		self.frame_camera = Tkinter.Frame(window)
		self.lab_camera = Tkinter.Label(self.frame_camera, text ="Camera").grid(row=0,column=0)
		
		self.lab_url = Tkinter.Label(self.frame_camera, text = "URL Yawcam: ").grid(row=1,column=0)
		
		self.urlValue = Tkinter.StringVar()
		self.urlValue.set("http://"+socket.gethostbyname(socket.gethostname())+":8888/out.jpg")
		self.tbox_URL = Tkinter.Entry(self.frame_camera, textvariable = self.urlValue, width=50)
		self.tbox_URL.grid(row=1,column=2,padx=5,pady=5)
		
		self.btn_capture = Tkinter.Button(self.frame_camera, text ="Capture", width=10, command=self.btnCapture)
		self.btn_capture.grid(row=1,column=3,padx=5,pady=5)
		
		self.lab_dir = Tkinter.Label(self.frame_camera, text = "Captured Directory: ").grid(row=2,column=0)
		
		self.dirValue = Tkinter.StringVar()
		self.dirValue.set("./capture/")
		self.tbox_dir = Tkinter.Entry(self.frame_camera, textvariable = self.dirValue, width=50)
		self.tbox_dir.grid(row=2,column=2,padx=5,pady=5)
		
		self.btn_dir = Tkinter.Button(self.frame_camera, text ="Change Directory", width=15, command=self.btnDirectory)
		self.btn_dir.grid(row=2,column=3,padx=5,pady=5)
		############################################################################################
		
		###################################RPC SERVER###############################################
		self.frame_rpc_server = Tkinter.Frame(window)
		self.rpc_server = Tkinter.Label(self.frame_rpc_server, text ="RPC SERVER").grid(row=0,column=0)
		
		self.lab_ipserver = Tkinter.Label(self.frame_rpc_server, text = "IP RPC SERVER: ").grid(row=1,column=0)
		
		self.ipserver = Tkinter.StringVar()
		self.ipserver.set("http://192.168.15.223")
		self.tbox_ipserver = Tkinter.Entry(self.frame_rpc_server, textvariable = self.ipserver, width=50)
		self.tbox_ipserver.grid(row=1,column=1,padx=5,pady=5)
		
		self.btn_1 = Tkinter.Button(self.frame_rpc_server, text ="?????", width=10, command=self.btnResetArduino)
		self.btn_1.grid(row=1,column=2,padx=5,pady=5)
		############################################################################################
		
		###################################STB LOG##################################################
		self.frame_STB_LOG = Tkinter.Frame(window)
		self.STB_LOG = Tkinter.Label(self.frame_STB_LOG, text ="STB LOG").grid(row=0,column=0)
		
		self.lab_ipSTB = Tkinter.Label(self.frame_STB_LOG, text = "IP STB: ").grid(row=1,column=0)
		
		self.ipSTB = Tkinter.StringVar()
		self.ipSTB.set("http://192.168.15.223")
		self.tbox_ipSTB = Tkinter.Entry(self.frame_STB_LOG, textvariable = self.ipSTB, width=50)
		self.tbox_ipSTB.grid(row=1,column=1,padx=5,pady=5)
		
		self.btn_2 = Tkinter.Button(self.frame_STB_LOG, text ="?????", width=10, command=self.btnResetArduino)
		self.btn_2.grid(row=1,column=2,padx=5,pady=5)
		############################################################################################
		
		##########################################Grid##############################################
		self.frame_serial.grid(row=0,column=0, sticky="NW")
		self.frame_remote.grid(row=1,column=0, sticky="NW")
		self.frame_delay.grid(row=2,column=0,sticky="NW")
		self.frame_AC.grid(row=3,column=0, sticky="NW")
		self.frame_camera.grid(row=4,column=0, sticky="NW", columnspan=2)
		self.frame_command.grid(row=0,column=1, sticky="NW", rowspan=2)
		#self.frame_rpc_server.grid(row=5,column=0, sticky="NW")
		#self.frame_STB_LOG.grid(row=5,column=1, sticky="NW")	
		#self.frame_log.grid(row=3,column=0,sticky="wn", columnspan=2)
		window.config(menu=menubar)
		############################################################################################
		
		########################################INITIATE############################################
		self.RUN_UI()
		self.btn_stop.config(state="disabled")
		############################################################################################
		
	#########################################Serial Function###########################################
	def ConnectArduinoSerial(self,ser):
		print("Connecting to Arduino.....")
		for i in range (1,5):
			rv=ser.readline()
			print("Loading...")
			
			print (rv.decode("utf-8")) #doesn't show anything ???
			ser.flushInput()
			time.sleep(1) # Delay for one tenth of a second
			Str=rv.decode("utf-8")
			
			if Str[0:5]=="Ready":  
				  print("Get Arduino Ready !")
				  return True
				  break
		return False
	###################################################################################################

	#########################################BUTTON FUNCTION###########################################
	def btnUP(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push UP Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("u")
		
	def btnDown(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Down Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("d")
		
	def btnLeft(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Left Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("l")
		
	def btnRight(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Right Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("r")
		
	def btnOK(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push OK Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("o")
		
	def btnPower(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Power Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("p")

	def btnMenu(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Menu Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("m")
		
	def btnHome(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Home Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("h")

	def btnSubmitDelay(self):
		delayTime=self.delayValue.get()
		if delayTime.isdigit():
			if int(delayTime) > 0:
				#add to listbox_command
				self.listbox_command.insert(self.ctr_command,"Delay for " + delayTime + " Second(s)")
				self.listbox_command.yview(self.ctr_command)
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
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("n")
		
	def btnACoff(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Turn AC Off")
		self.listbox_command.yview(self.ctr_command)
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
			if self.urlValue.get() != "" and self.dirValue.get() != "" :
				#Change UI
				self.RUN_UI()
				#Run Operation
				self.operationTask=operationTask(self.command_list,self.ser,self.urlValue,self.dirValue,self.sbox_cycle.get())
				self.operationTask.operation_status="run"
				self.operationTask.start()
			else:
				tkm.showerror("Error", "URL or Directory cannot be blank")	
		else:
			tkm.showerror("Error", "No Command Setup")	
	
	def btnConnect(self):
		try:
			self.port=self.serialValue.get()
			self.ser = serial.Serial(self.port[:4], 9600, timeout=2) # Establish the connection on a specific port
			if self.ConnectArduinoSerial(self.ser) :
				print("success")
				self.STOP_UI()
				self.btn_connect.config(state="disabled")
				self.oMenu_serial.config(state="disabled")
			else:
				print("fail")
		except serial.SerialException:
			print ("Port not Found")
	
	def btnCapture(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Capture Monitor")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("cap")
		
	def btnResetArduino(self):
		self.ser.write("f".encode('utf-8'))
		
	def btnDirectory(self):
		window.directory = filedialog.askdirectory()
		self.dirValue.set(window.directory)
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
			if child.winfo_class() == 'Button' or child.winfo_class() == 'Spinbox':
				child.configure(state='disable')
		#disable Frame Camera
		for child in self.frame_camera.winfo_children():
			if child.winfo_class() == 'Button' or child.winfo_class() == 'Entry':
				child.configure(state='disable')
		##############################################################
		#enable button which necessary
		self.btn_stop.config(state="normal")	
		
	def STOP_UI(self):
		######################enabled all button######################
		#enable Frame Remote
		for child in self.frame_remote.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		#enable Frame AC
		for child in self.frame_AC.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		#enable Frame Delay
		for child in self.frame_delay.winfo_children():
			if child.winfo_class() == 'Button':
				child.configure(state='normal')
		#enable Frame Command
		for child in self.frame_command.winfo_children():
			if child.winfo_class() == 'Button' or child.winfo_class() == 'Spinbox':
				child.configure(state='normal')
		#enable Frame Camera
		for child in self.frame_camera.winfo_children():
			if child.winfo_class() == 'Button' or child.winfo_class() == 'Entry':
				child.configure(state='normal')
		##############################################################
		#disable button which necessary
		self.btn_stop.config(state="disable")
	############################################################################################
	
	##########################################Menu FUNCTION#####################################
	def btnSaveCommand(self):
		f = filedialog.asksaveasfile(mode='w', defaultextension=".trzats")
		if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
			print ("Save Cancel")
			return
		else:
			#write the file
			for command in self.command_list:
				f.write(command)
				f.write("\n")
			f.close() 
			print ("Save Success")

	def btnLoadCommand(self):
		filePath = filedialog.askopenfile(mode='rt', filetypes=(("Tranzas ATS File", "*.trzats"),("All files", "*.*")))
		if filePath is None: # askopenfilename return `None` if dialog closed with "cancel".
			print ("Load Cancel")
		else:
			self.btnClear()
			#read file
			with filePath as f:
				line=f.readlines()
				line = [x.strip() for x in line]
			f.close()
			#process to command
			for command in line:
				self.stringToCommand(command)
			print("Load Success")
		
	def stringToCommand(self,cmd):
		if cmd=="u":
			self.btnUP()
		if cmd=="d":
			self.btnDown()
		if cmd=="l":
			self.btnLeft()
		if cmd=="r":
			self.btnRight()
		if cmd=="o":
			self.btnOK()
		if cmd=="p":
			self.btnPower()
		if cmd=="m":
			self.btnMenu()
		if cmd=="h":
			self.btnHome()
		if cmd=="n":
			self.btnACon()
		if cmd=="f":
			self.btnACoff()
		if cmd=="cap":
			self.btnCapture()
		if cmd.isdigit():
			self.delayValue.set(int(cmd))
			self.btnSubmitDelay()
	############################################################################################
	
window = Tkinter.Tk()
window.title("Tranzas STB Automation Test Ver 0.3")
main_ui=GuiPart(window)
window.mainloop()