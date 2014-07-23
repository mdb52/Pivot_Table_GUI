# -*- coding: utf-8 -*-
"""
@author: matthew belley
"""

from __future__ import division


# These allow mpl in PyQt
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtCore import QSize

import numpy as np
import seaborn as sb
from pylab import *
import pandas as pd
import itertools
import matplotlib._pylab_helpers
from PyQt4 import *

import pyqtgraph as pg

"""
This loads CSV of all fiber data and plots various parameters from pivot tables

Must use SELF.COMMAND when you want to access that value outside of the function (gets stored to the class)

GUI V1: beta just barely works
    V2: improving the "Real Time capability"
    V3: uses pyqtplot -- for real time plot, and fixed GUI layout
        started using GIT and GIT-HUB

"""

def setSeabornParams():
	# Talk seems to be best choice for font size
	sb.set_context("talk")

	# use "cubehelix" colormap for printing; hls is used for SB
	# sb.palplot(sb.color_palette("jet", 8))
	sb.set_palette(sb.color_palette("jet", 8))
	sb.set_palette("jet",8)

def loadData(fname):
	data = pd.read_csv(fname)
	return data;

def filterGoodValues(data):
	print('Size before filtering: '+repr(np.shape(data)))
	print('FILTERING PERFORMED')
	# Remove rows that have yes in either column: 
	# 'Not a new calibration?' and 'Diode Measured Scatter or Cerenov?'
	data = data[data.loc[:,'Not a new calibration?'] != 'Yes']
	data = data[data.loc[:,'Diode Measured Scatter or Cerenkov?'] != 'Yes']
	print('Size after filtering: '+repr(np.shape(data)))
	return data

def plotBoxValues(data, value_list, row, col, showMPL):
	for xx in value_list:
		#Make a pivot table for every value

		table1 = pd.pivot_table(data, values=xx, 
			rows=row, cols=col, dropna=True)

		# drop if all data is missing in an axis
		print('Size before removing nan: '+repr(np.shape(table1)))
		table1 = table1.dropna(axis=0, how='all')
		table1 = table1.dropna(axis=1, how='all')
		print('Size after removing nan: '+repr(np.shape(table1)))

		if showMPL == True:
			
			# GET N
			N_table1 = table1.count(axis=0)
			N_table1_T = table1.count(axis=1)

			# Get Avg
			meanX = table1.mean()
			meanY = table1.T.mean()

			print('Mean x, y: ' + repr(meanX) + ', ' + repr(meanY))

			p1=figure(figsize=(11,8))
			sb.set_palette("jet",8)
			table1.boxplot()
			title(xx + ' By '+col)
			yscale('log')
			xlabel(col, fontsize=12, fontweight='bold')
			
			locs, labels = xticks()
			ymin, ymax = ylim()

			for index in range(len(locs)):
				text(locs[index], 1.2*ymin, 'N: '+repr(N_table1.iloc[index]), 
						horizontalalignment='center')
				text(locs[index], 2*ymin, '$\\bar{x}$: ' +'%.2g'%meanX.iloc[index],
						horizontalalignment='center')


			p2=figure(figsize=(11,8))
			sb.set_palette("jet",8)
			table1.T.boxplot()
			title(xx + ' By '+row)
			yscale('log')
			xticks(rotation=90)
			xlabel(row, fontsize=12, fontweight='bold')
			
			locs, labels = xticks()
			ymin, ymax = ylim()

			for index in range(len(locs)):
				text(locs[index], 1.2*ymin, 'N: '+repr(N_table1_T.iloc[index]), 
						horizontalalignment='center')

				text(locs[index], 2*ymin, '$\\bar{x}$: ' +'%.2g'%meanY.iloc[index],
						horizontalalignment='center')
			show()

		return table1;

class Table(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Table, self).__init__(parent)
        layout = QtGui.QGridLayout() 
        self.table = QtGui.QTableWidget(self)	# Parent of table
        layout.addWidget(self.table, 0, 0)
        self.setLayout(layout)

class MainWindow(QtGui.QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()

		self.initUI()

		self.loadedData = []
		self.filteredData = [] 
		self.checkBoxList = []
		self.pivotData = []
	
	def setLoadedData(self, setValue):
		self.loadedData = setValue

	def setFilteredData(self, setValue):
		self.filteredData = setValue

	def setPivotData(self, setValue):
		self.pivotData = setValue

	def initUI(self):
	
		self.setWindowTitle('Main Program')

		exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
		exitAction.triggered.connect(QtGui.qApp.quit)

		self.statusBar()

		# For tabbed widgets, do not specify a parent
		mainWidget = QtGui.QWidget()
	
		# Quit Button
		btn_quit = QtGui.QPushButton('Quit', mainWidget)
		btn_quit.clicked.connect(QtCore.QCoreApplication.instance().quit)
		btn_quit.setToolTip('This is a <b>QPushButton</b> widget')
		btn_quit.resize(btn_quit.sizeHint())
		#btn_quit.move(0,550)	# x-y location
	
		# Plot data button
		btnPlot = QtGui.QPushButton('Plot Data', mainWidget)
		btnPlot.setToolTip('This will plot the <b>Displayed</b> Data')
		btnPlot.resize(btnPlot.sizeHint())
		#btnPlot.move(0,150)

		btnFilter = QtGui.QPushButton('Filter Out Check Boxes', mainWidget)
		btnFilter.setToolTip('You can remove types of data from analysis here')
		btnFilter.resize(btnFilter.sizeHint())
		#btnFilter.move(0,100)

		# LOAD DATA AND SAVE TO A VARIABLE
		openFile = QtGui.QAction(QtGui.QIcon('open.png'), 'Open', mainWidget)
		openFile.setShortcut('Ctrl+O')
		openFile.setStatusTip('Open new File')
		openFile.triggered.connect(self.openFileDialog)

		# Define what happens when buttons are clicked
		btnFilter.clicked.connect(self.filterClicked)
		btnPlot.clicked.connect(self.plotClicked)

		# Drop down select combo box
		lbl1 = QtGui.QLabel('Series', mainWidget)
		self.combo = QtGui.QComboBox(mainWidget)

		# Drop down select combo box
		lbl2 = QtGui.QLabel('X-Axis', mainWidget)
		self.combo2 = QtGui.QComboBox(mainWidget)
		
		# Troubleshooting print button
		btn_test = QtGui.QPushButton('Troubleshoot', mainWidget)
		btn_test.resize(btn_test.sizeHint())
		btn_test.clicked.connect(self.troubleshootClicked)

		# Check box to show MPL figures in addition to real time
		self.checkMPL = QtGui.QCheckBox("Enable MPL")		

		# Plot Widget
		self.plotWindow = pg.PlotWidget()

		# Grid LAYOUT		4 rows, 8 columns
		nRows = 8; nCols = 8
		layout = QtGui.QGridLayout()
		# addItem (self, QLayoutItem item, int row, 
			# int column, int rowSpan = 1, int columnSpan = 1, Qt.Alignment alignment = 0)
		layout.addWidget(btn_test, 0, 0)	# Goes in upper left
		layout.addWidget(btnFilter, 1, 0)	# Goes in middle left
		layout.addWidget(btnPlot, 2, 0)
		layout.addWidget(btn_quit, nRows, 0)	# Bottom left
		# Add a spacer and allow it to expand
		# layout.addItem(QtGui.QSpacerItem(0, 0, vPolicy = QSizePolicy.Expanding, 
			#hPolicy = QSizePolicy.Expanding), 0, 1, nRows, nCols)		#	
		layout.addWidget(self.checkMPL, 3, 0)		
		mainWidget.setLayout(layout)
		layout.addWidget(lbl1, 4, 1)
		layout.addWidget(self.combo, 4, 0)
		layout.addWidget(lbl2, 5, 1)
		layout.addWidget(self.combo2, 5, 0)
		layout.addWidget(self.plotWindow, 0, 2, nRows, nCols)

		# Add a tab bar with widgets (tab 1 is options and figure, tab 2 is table)
		self.tabBar = QtGui.QTabWidget(self)
		self.tabBar.addTab(mainWidget, "Plot Settings")

		# Add MENU Bar - goes mainWindow
		menuBar = self.menuBar()
		fileMenu = menuBar.addMenu('&File')
		fileMenu.addAction(openFile)
		fileMenu.addAction(exitAction)

		# SET Tabbed WIDGET AS CENTRAL
		self.setCentralWidget(self.tabBar)

		self.setGeometry(50, 50, 1200, 600)	# x,y for corner and then x-y widths
		self.show()
	
	def plotReal(self, axes):
		self.plotWindow.clear()		# refresh if old data is here
		print(np.asarray(self.pivotData))
		xVals = self.pivotData.columns.tolist()
		xVals = [str(x) for x in xVals]
		yVals = self.pivotData.index.tolist()
		yVals = [str(x) for x in yVals]
		

		print('x: '+repr(xVals))
		print('y: '+repr(yVals))
		
		# Delete any old legends
		self.plotWindow.addLegend((100,100))	# This must go above the plot calls
		colorValues = ['r','g','b','c','m','y','k','w']
		colorCycles = itertools.cycle(colorValues)
		for ind, each in enumerate(np.asarray(self.pivotData)):
			color = colorCycles.next()
			self.plotWindow.plot(each, name=yVals[ind], symbol='o', symbolPen = color, pen =color)
		
		self.plotWindow.setLabel('left', self.valuePlot)
		self.plotWindow.setLabel('bottom', self.combo2.currentText())
	
		# Make tick labels
		xAxis = self.plotWindow.getAxis('bottom')
		newTicks = zip(range(len(xVals)), (xVals))
		print('New Ticks: '+repr(newTicks))
		# xAxis.setStyle(autoExpandTextSpace = 1)		# not out until version 0.9.9
		xAxis.setTicks([newTicks]) 		# 

		
	def troubleshootClicked(self):
		print('Combo text value: '+repr(str(self.combo.currentText())))
		listDataToPlot = []
		for index, each in enumerate(self.checkBoxList):
			if each.checkState() > 0:
				# append a list of indices where boxes are checked!
				listDataToPlot.append(index)
		print('Indices of Data to Plot from checkboxes: '+repr(listDataToPlot))
		print('These are the text objects: '+str(self.loadedData.columns[listDataToPlot].tolist()))

	def plotClicked(self):
		sender = self.sender()
		self.statusBar().showMessage(sender.text() + ' was pressed')
		
		listDataToPlot = []
		
		# Check if we are going to enable Matplotlib
		if self.checkMPL.checkState() > 0:
			MPLFlag = True;
		else: 
			MPLFlag = False

		for index, each in enumerate(self.checkBoxList):
			if each.checkState() > 0:
				# append a list of indices where boxes are checked!
				listDataToPlot.append(index)
	
		self.valuePlot =self.loadedData.columns[listDataToPlot].tolist()
		try:
			self.setPivotData( 
					plotBoxValues(self.filteredData, 
						self.valuePlot, 
						str(self.combo.currentText()), str(self.combo2.currentText()), 
						MPLFlag))
			

		except Exception, err:
			errorWin = QtGui.QMessageBox(self)
			errorWin.setText('Error: Try Filtering the data first')
			errorWin.show()
			print('Failed for this reason: ')
			print(repr(err))
			pass

		# PLOT FIGURE
		self.plotReal(self)
	
	def filterClicked(self):
		
		sender = self.sender()
		self.statusBar().showMessage(sender.text() + ' was pressed')
		try:
			self.setFilteredData(filterGoodValues(self.loadedData))
		except:
			errorWin = QtGui.QMessageBox(self)
			errorWin.setText('Error: Try loading data first')
			errorWin.show()

	def openFileDialog(self):
		# SELF IS ALWAYS THE NAME OF THE CLASS
		fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 
				'/home')
		print('Opening File: '+repr(fname))
		data = loadData(str(fname))
		
		# Store the values
		self.setLoadedData(data);
	
		# Create a checkbox WIDGET to store this data
		self.checkWidget = QtGui.QWidget()
		self.filterWidget = QtGui.QWidget()

		checkWidgetList = [self.checkWidget, self.filterWidget]
		nameWidgetList = ["Plot Values", "Filter Values"]

		# Delete the old tabs, if there are more than 3 tabs total now 
		if self.tabBar.count() >= 4:
			# First try to delete existing tabs from previous runs
			# Tabs are numbers 1, 2
			self.tabBar.removeTab(1)
			self.tabBar.removeTab(1)

		# Combo box for FILTERING choices
		counts =0;
		# Reset any values that may have been set before
		try:
			del self.checkBoxList[:]
		except:
			pass
		self.combo.clear(); self.combo2.clear();
		for number, widget in enumerate(checkWidgetList):
			layout = QtGui.QGridLayout()
			for index, each in enumerate(data.columns):
				# Fill combo boxes, only once
				if number == 1:
					self.combo.addItem(each)
					self.combo2.addItem(each)

				# Make checkboxes for values - first half belowng to "Plot Values", second half "Filter"
				self.checkBoxList.append(QtGui.QCheckBox(each, widget))
				self.checkBoxList[counts].sizeHint()
				# make a grid, with 2 columns
				layout.addWidget(self.checkBoxList[counts], floor(counts/2), counts % 2)
				counts+=1;
			
			widget.setLayout(layout)

			# add a tab showing these values -- 2 tabs total
			self.tabBar.insertTab(number+1, widget, nameWidgetList[number])

		# Make a TABLE
		t = Table()		# Do not put a parent here?
		t.table.setColumnCount(len(data.columns))
		t.table.setRowCount(len(data.index))
		for i in range(len(data.index)):
			for j in range(len(data.columns)):
				t.table.setItem(i,j,
						QtGui.QTableWidgetItem(str(data.iget_value(i, j))))
		for i, value in enumerate(data.columns):
			t.table.setHorizontalHeaderItem(i, QtGui.QTableWidgetItem(str(value)))
	
		# Show the table
		if self.tabBar.count() >= 4:
			self.tabBar.removeTab(3)
			self.tabBar.addTab(t, "Updated Table")
		else:
			# Set for first time
			self.tabBar.addTab(t, "Table")	# Add Table Tab
			

		# Message Window
		multiPickWin = QtGui.QMessageBox(self)
		multiPickWin.setText('You can only choose <b>ONE</b> check box at a time')
		multiPickWin.show()
		
if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	
	setSeabornParams()

	w = MainWindow()	

	sys.exit(app.exec_())

