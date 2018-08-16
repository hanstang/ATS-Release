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
import random
from tkinter import filedialog, Menu
from adb import ADB

class operationTask(threading.Thread):
	operation_status="stop" #"run" and "stop"
	log_file_name=""
	def __init__(self, listCmd, serial, yawcamURL, captureDir, cycles):
		threading.Thread.__init__(self)
		self.command_list = listCmd
		self.ser = serial
		self.yawcamURL = yawcamURL.get()
		self.captureDir = captureDir.get()
		self.cycles = cycles
		self.log_file_name=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		
	def run(self):
		self.ser.flushInput() #clear all content in serial port
		self.ser.flushOutput() #clear all content in serial port
		counter_loop=1
		os.system('cls' if os.name == 'nt' else 'clear')
		while self.operation_status=="run":
			self.printAndLog("Cycle : " + str(counter_loop))
			self.printAndLog("Time  : " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			self.printAndLog("===================================================")
			
			for command in self.command_list:
				if command.isdigit(): #Delay
					self.printAndLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : Waiting for "+command+" Second(s)")
					
					#looping for timer and check is stop button pushed
					ctr_time=0
					while True:
						ctr_time+=1
						time.sleep(1)
						if ctr_time >= int(command) or self.operation_status=="stop":
							break
					#time.sleep(int(command))
				elif command[:2]=="DR": #Delay Random
					proCMD=command.split(",")
					delayTime=random.randint(int(proCMD[1]),int(proCMD[2]))
					self.printAndLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" : Random Waiting from " + str(proCMD[1]) + " to " + str(proCMD[2]) + " for "+ str(delayTime) +" Second(s)")
					
					#looping for timer and check is stop button pushed
					ctr_time=0
					while True:
						ctr_time+=1
						time.sleep(1)
						if ctr_time >= int(delayTime) or self.operation_status=="stop":
							break
					#time.sleep(int(delayTime))
					
				elif command=="cap": #Capture 
					self.printAndLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +self.capturingMonitor(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
					time.sleep(int(1))
				else: #Arduino command
					self.ser.write(command.encode('utf-8'))
					time.sleep(int(1))
					ctr_try=0
					while True:
						ctr_try+=1
						rv=self.ser.readline()
						#print (rv.decode("utf-8"))
						self.ser.flushInput()
						if self.chekerArduinoReturn(rv,command):
							self.printAndLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +self.readCommandCode(command))
							break
						else:
							self.printAndLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +self.readCommandCode(command) + " Failed (" + str(ctr_try) + ")")
							if ctr_try < 3:
								self.ser.write(command.encode('utf-8'))
								time.sleep(int(1))
							else: 
								break
					time.sleep(int(1))
					
				if self.operation_status=="stop":
					self.printAndLog(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+ " : " +"Button Stop Pushed!!!!!!!!!!")
					break
			self.printAndLog("===================================================")
			if counter_loop >= int(self.cycles) and self.operation_status=="run":
				self.operation_status="stop"
				self.printAndLog("*************************Cycles Has been Finished*************************")
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
		if cmd=="a":
			return "FFwd button pushed"
		if cmd=="b":
			return "Rewind button pushed"
		if cmd=="c":
			return "Play/Pause button pushed"
		if cmd=="e":
			return "Stop button pushed"
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
	
	def chekerArduinoReturn(self, input, command):
		#print(input.decode("utf-8"))
		if input.decode("utf-8")[:2] == "Up" and command == "u":
			return True
		if input.decode("utf-8")[:4] == "Down" and command == "d":
			return True
		if input.decode("utf-8")[:4] == "Left" and command == "l":
			return True
		if input.decode("utf-8")[:5] == "Right" and command == "r":
			return True
		if input.decode("utf-8")[:2] == "OK" and command == "o":
			return True
		if input.decode("utf-8")[:5] == "power" and command == "p":
			return True
		if input.decode("utf-8")[:4] == "menu" and command == "m":
			return True
		if input.decode("utf-8")[:4] == "home" and command == "h":
			return True
		if input.decode("utf-8")[:5] == "AC ON" and command == "n":
			return True
		if input.decode("utf-8")[:6] == "AC Off" and command == "f":
			return True
		if input.decode("utf-8")[:4] == "ffwd" and command == "a":
			return True
		if input.decode("utf-8")[:6] == "rewind" and command == "b":
			return True
		if input.decode("utf-8")[:9] == "playpause" and command == "c":
			return True
		if input.decode("utf-8")[:4] == "stop" and command == "e":
			return True
		return False
		
	def printAndLog(self,text):
		#print on cmd
		print (text)
		#put on notepad
		if not os.path.exists(self.captureDir):
			os.makedirs(self.captureDir)
			
		f = open(self.captureDir+"/ATS_LOG_"+self.log_file_name+".txt","a+")
		f.write(text + "\n")
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
		self.frame_remote = Tkinter.LabelFrame(window, text="Remote Control", bg="#5F7CBD")
		#self.lab_remote = Tkinter.Label(self.frame_remote, text ="Remote Control").grid(row=0,column=0,sticky="NW")
        
		self.btn_up = Tkinter.Button(self.frame_remote, text ="Up", width=8, command=self.btnUP, bg="#BD6F5F")
		self.btn_up.grid(row=1,column=1,padx=5,pady=5,sticky="NW")
        
		self.btn_down = Tkinter.Button(self.frame_remote, text = "Down", width=8, command=self.btnDown, bg="#BD6F5F")
		self.btn_down.grid(row=3,column=1,padx=5,pady=5,sticky="NW")
        
		self.btn_left = Tkinter.Button(self.frame_remote, text ="Left", width=8, command=self.btnLeft, bg="#BD6F5F")
		self.btn_left.grid(row=2,column=0,padx=5,pady=5,sticky="NW")
        
		self.btn_right = Tkinter.Button(self.frame_remote, text ="Right", width=8, command=self.btnRight, bg="#BD6F5F")
		self.btn_right.grid(row=2,column=2,padx=5,pady=5,sticky="NW")
        
		self.btn_ok = Tkinter.Button(self.frame_remote, text ="OK", width=8, command=self.btnOK)
		self.btn_ok.grid(row=2,column=1,padx=5,pady=5,sticky="NW")
        
		self.btn_power = Tkinter.Button(self.frame_remote, text ="Power", width=8, command=self.btnPower)
		self.btn_power.grid(row=1,column=3,padx=5,pady=5,sticky="NW")
       
		self.btn_menu = Tkinter.Button(self.frame_remote, text ="Menu", width=8,command=self.btnMenu)
		self.btn_menu.grid(row=2,column=3,padx=5,pady=5,sticky="NW")
       
		self.btn_home = Tkinter.Button(self.frame_remote, text = "Home", width=8,command=self.btnHome)
		self.btn_home.grid(row=3,column=3,padx=5, pady=5,sticky="NW")
		
		self.btn_forward = Tkinter.Button(self.frame_remote, text = "FFwd", width=8 , bg="#BDB0AA", command=self.btnFFwd)
		self.btn_forward.grid(row=1,column=2,padx=5, pady=5, sticky="NW")
		
		self.btn_rewind = Tkinter.Button(self.frame_remote, text = "Rewind", width=8 , bg="#BDB0AA", command=self.btnRewind)
		self.btn_rewind.grid(row=1,column=0,padx=5, pady=5, sticky="NW")
		
		self.btn_playPause = Tkinter.Button(self.frame_remote, text = "Play/Pause", width=8 , bg="#BDB0AA", command=self.btnPlayPause)
		self.btn_playPause.grid(row=3,column=0,padx=5, pady=5, sticky="NW")
		
		self.btn_stop = Tkinter.Button(self.frame_remote, text = "Stop", width=8 , bg="#BDB0AA", command=self.btnRemoteStop)
		self.btn_stop.grid(row=3,column=2,padx=5, pady=5, sticky="NW")
		############################################################################################

		##########################################AC################################################
		self.frame_AC = Tkinter.LabelFrame(window, text ="AC" , bg="#5F7CBD")
		#self.lab_AC = Tkinter.Label(self.frame_AC, text ="AC").grid(row=0,column=0,sticky="NW")

		self.btn_AC_on = Tkinter.Button(self.frame_AC, text ="ON", width=10, command=self.btnACon)
		self.btn_AC_on.grid(row=1,column=0,padx=5,pady=5,sticky="NW")

		self.btn_AC_off = Tkinter.Button(self.frame_AC, text ="OFF", width=10, command=self.btnACoff)
		self.btn_AC_off.grid(row=1,column=1,padx=5,pady=5,sticky="NW")
		############################################################################################

		#########################################Command############################################
		self.frame_command = Tkinter.LabelFrame(window , text ="Command", bg="#5F7CBD")
		#self.lab_command = Tkinter.Label(self.frame_command, text ="Command", bg="#5F7CBD").grid(row=0,column=0,sticky="NW")

		self.listbox_command = Tkinter.Listbox(self.frame_command, width=30, height=20)
		self.listbox_command.grid(row=1,column=0,pady=5,padx=(10,0), columnspan=2,sticky="NSEW")
		
		self.scrollbar_command = Tkinter.Scrollbar(self.frame_command, command=self.listbox_command.yview)
		self.scrollbar_command.grid(row=1,column=2,padx=(0,10),pady=5,sticky="NSEW")
		
		self.listbox_command.configure(yscrollcommand = self.scrollbar_command.set)

		self.btn_run = Tkinter.Button(self.frame_command, text ="Run", width=10, command=self.btnRun)
		self.btn_run.grid(row=2,column=0,padx=(10,5),pady=5,sticky="NWE")

		self.btn_stop = Tkinter.Button(self.frame_command, text ="Stop", width=10, command=self.btnStop)
		self.btn_stop.grid(row=2,column=1,padx=5,pady=5,sticky="NWE")

		self.btn_clear = Tkinter.Button(self.frame_command, text ="Clear", width=10, command=self.btnClear)
		self.btn_clear.grid(row=3,column=0,padx=(10,5),pady=5,sticky="NWE")
		
		self.btn_reset_arduino = Tkinter.Button(self.frame_command, text ="Reset Arduino", width=10, command=self.btnResetArduino)
		self.btn_reset_arduino.grid(row=3,column=1,padx=5,pady=5,sticky="NWE")
		
		self.lab_cycle = Tkinter.Label(self.frame_command, text ="Cycle : " , bg="#5F7CBD").grid(row=4,column=0,sticky="E")
		self.sbox_cycle = Tkinter.Spinbox(self.frame_command, width=10, from_=1, to=100000)
		self.sbox_cycle.grid(row=4,column=1,padx=5,pady=5,sticky="NW")

		self.btn_stop.config(state="disabled") #disabled and normal
		############################################################################################

		#########################################Delay##############################################
		self.frame_delay = Tkinter.LabelFrame(window, text ="Delay" , bg="#5F7CBD")
		
		self.lab_fixDelay = Tkinter.Label(self.frame_delay, text ="Fixed Delay", bg="#5F7CBD").grid(row=0,column=0,sticky="NW")
		
		self.lab_timeDelay = Tkinter.Label(self.frame_delay, text ="Time : ", bg="#5F7CBD").grid(row=1,column=0,sticky="NSE")
		
		self.delayValue = Tkinter.StringVar()
		self.delayValue.set(1)
		
		self.sbox_delay = Tkinter.Spinbox(self.frame_delay, width=10, from_=1, to=100000, textvariable=self.delayValue)
		self.sbox_delay.grid(row=1,column=1,padx=5,pady=5,sticky="NSW")
		
		self.lab_second = Tkinter.Label(self.frame_delay, text ="Second(s)" , bg="#5F7CBD").grid(row=1,column=2,sticky="NSEW")
		self.btn_submit = Tkinter.Button(self.frame_delay, text ="Submit", width=10, command=self.btnSubmitDelay).grid(row=1,column=3,padx=5,pady=5,sticky="NW")
		
		############################################################################################
		
		###################################Random Delay#############################################
		self.lab_random_delay = Tkinter.Label(self.frame_delay, text ="Random Delay" , bg="#5F7CBD").grid(row=2,column=0,sticky="NW")
		
		self.lab_min_delay = Tkinter.Label(self.frame_delay, text ="Minimum : " , bg="#5F7CBD").grid(row=3,column=0,sticky="NSE")
		
		self.delayValueMin = Tkinter.StringVar()
		self.delayValueMin.set(1)
		self.sbox_delay_min = Tkinter.Spinbox(self.frame_delay, width=10, from_=1, to=100000, textvariable=self.delayValueMin)
		self.sbox_delay_min.grid(row=3,column=1,padx=5,pady=5,sticky="NSW")
		Tkinter.Label(self.frame_delay, text ="Second(s)" , bg="#5F7CBD").grid(row=3,column=2,sticky="NSEW")
		
		self.lab_min_delay = Tkinter.Label(self.frame_delay, text ="Maximum : " , bg="#5F7CBD").grid(row=3,column=3,sticky="NSE")
		
		self.delayValueMax = Tkinter.StringVar()
		self.delayValueMax.set(10)
		self.sbox_delay_max = Tkinter.Spinbox(self.frame_delay, width=10, from_=2, to=100000, textvariable=self.delayValueMax)
		self.sbox_delay_max.grid(row=3,column=4,padx=5,pady=5,sticky="NSW")
		Tkinter.Label(self.frame_delay, text ="Second(s)" , bg="#5F7CBD").grid(row=3,column=5,sticky="NSEW")
		
		self.btn_submit_random = Tkinter.Button(self.frame_delay, text ="Submit", width=10, command=self.btnSubmitDelayRandom).grid(row=3,column=6,padx=5,pady=5,sticky="NW")
		############################################################################################
		
		##################################Serial Port Setting#######################################
		self.frame_serial = Tkinter.LabelFrame(window, text="Serial Port Setting" , bg="#5F7CBD")
		#self.lab_serial = Tkinter.Label(self.frame_serial, text ="Serial Port Setting").grid(row=0,column=0,sticky="NW")
		
		self.ports = list(serial.tools.list_ports.comports())	#get port list
		
		self.serialValue = Tkinter.StringVar()
		self.serialValue.set(self.ports[0])
		
		self.oMenu_serial = Tkinter.OptionMenu(self.frame_serial, self.serialValue, *self.ports)
		self.oMenu_serial.grid(row=1,column=0,padx=5,pady=5,sticky="NW")
		
		self.btn_connect = Tkinter.Button(self.frame_serial, text ="Connect", width=10, command=self.btnConnect)
		self.btn_connect.grid(row=1,column=1,padx=5,pady=5,sticky="NSW")
		############################################################################################
		
		################################Camera######################################################
		self.frame_camera = Tkinter.LabelFrame(window, text="Camera" , bg="#5F7CBD")
		#self.lab_camera = Tkinter.Label(self.frame_camera, text ="Camera").grid(row=0,column=0,sticky="NW")
		
		self.lab_url = Tkinter.Label(self.frame_camera, text = "URL Yawcam : ", bg="#5F7CBD").grid(row=1,column=0,sticky="NSE")
		
		self.urlValue = Tkinter.StringVar()
		#self.urlValue.set("http://"+socket.gethostbyname(socket.gethostname())+":8888/out.jpg")
		self.urlValue.set("http://localhost:8888/out.jpg")
		self.tbox_URL = Tkinter.Entry(self.frame_camera, textvariable = self.urlValue, width=50)
		self.tbox_URL.grid(row=1,column=2,padx=5,pady=5,sticky="NS")
		
		self.btn_capture = Tkinter.Button(self.frame_camera, text ="Capture", width=15, command=self.btnCapture)
		self.btn_capture.grid(row=1,column=3,padx=5,pady=5,sticky="NW")
		
		self.lab_dir = Tkinter.Label(self.frame_camera, text = "Captured & Log Directory : " , bg="#5F7CBD").grid(row=2,column=0,sticky="NSE")
		
		self.dirValue = Tkinter.StringVar()
		self.dirValue.set("./capture/")
		self.tbox_dir = Tkinter.Entry(self.frame_camera, textvariable = self.dirValue, width=50)
		self.tbox_dir.grid(row=2,column=2,padx=5,pady=5,sticky="NS")
		
		self.btn_dir = Tkinter.Button(self.frame_camera, text ="Change Directory", width=15, command=self.btnDirectory)
		self.btn_dir.grid(row=2,column=3,padx=5,pady=5,sticky="NW")
		############################################################################################
		
		#####################################ADB Screen Capture#####################################
		self.frame_adbscreen = Tkinter.LabelFrame(window, text="ADB Screen Capture" , bg="#5F7CBD")
		
		############################################################################################
		
		##########################################Grid##############################################
		self.frame_serial.grid(row=0,column=0, sticky="NSEW",padx=20,pady=10)
		self.frame_remote.grid(row=1,column=0, sticky="NSEW",padx=20,pady=10)
		self.frame_delay.grid(row=2,column=0,sticky="NSEW",padx=20,pady=10)
		self.frame_AC.grid(row=3,column=0, sticky="NSEW",padx=20,pady=10)
		self.frame_camera.grid(row=4,column=0, sticky="NSEW",padx=20,pady=10)
		self.frame_command.grid(row=0,column=2, sticky="NW", rowspan=4,padx=20,pady=10)
		self.frame_adbscreen.grid(row=0,column=1, sticky="NW",padx=20,pady=10)
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
			self.ser = serial.Serial(self.port[:5].replace(" ",""), 9600, timeout=2) # Establish the connection on a specific port
			if self.ConnectArduinoSerial(self.ser) :
				print("success")
				self.STOP_UI()
				self.btn_connect.config(state="disabled")
				self.oMenu_serial.config(state="disabled")
			else:
				print("fail")
		except serial.SerialException as e:
			print ("Port Error: " + str(e))
	
	def btnCapture(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Capture Monitor")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("cap")
		
	def btnResetArduino(self):
		self.ser.write("f".encode('utf-8'))
		rv=self.ser.readline()
		#print (rv.decode("utf-8"))
		self.ser.flushInput()
		
	def btnDirectory(self):
		window.directory = filedialog.askdirectory()
		self.dirValue.set(window.directory)
		
	def btnSubmitDelayRandom(self):
		if int(self.delayValueMin.get()) < int(self.delayValueMax.get()) :
			#add to listbox_command
			self.listbox_command.insert(self.ctr_command,"Delay Random from " + str(self.delayValueMin.get()) + " to " + str(self.delayValueMax.get()))
			self.listbox_command.yview(self.ctr_command)
			self.ctr_command+=1
			#add command to variable
			self.command_list.append("DR,"+str(self.delayValueMin.get())+","+str(self.delayValueMax.get()))
		else:
			tkm.showerror("Error", "Maximum Value Must be Greater than Minimum Value")
	
	def btnFFwd(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push FFwd Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("a")
		
	def btnRewind(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Rewind Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("b")
		
	def btnPlayPause(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Play/Pause Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("c")
	
	def btnRemoteStop(self):
		#add to listbox_command
		self.listbox_command.insert(self.ctr_command,"Push Stop Button")
		self.listbox_command.yview(self.ctr_command)
		self.ctr_command+=1
		#add command to variable
		self.command_list.append("e")
	
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
				line = f.readlines()
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
		if cmd[:2]=="DR":
			proCMD=cmd.split(",")
			self.delayValueMin.set(int(proCMD[1]))
			self.delayValueMax.set(int(proCMD[2]))
			self.btnSubmitDelayRandom()
		if cmd=="a":
			self.btnFFwd()
		if cmd=="b":
			self.btnRewind()
		if cmd=="c":
			self.btnPlayPause()
		if cmd=="e":
			self.btnRemoteStop()
	############################################################################################
	
window = Tkinter.Tk()
window.title("Tranzas STB Automation Test Ver 0.5")
window.configure(bg="#5F7CBD")
main_ui=GuiPart(window)

#update ui if operation finish
def update_ui():
	if main_ui.operationTask != "":
		if main_ui.operationTask.operation_status=="stop":
			main_ui.btnStop()
	window.after(1000,update_ui)

window.after(1,update_ui)
window.mainloop()


text=input("press enter key to exit")