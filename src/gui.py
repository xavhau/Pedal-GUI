import sys
import time
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QPolygon, QTransform
from PyQt5.QtCore import Qt, QRect, QPoint
from plugin_manager import PluginManager, Plugin, Parameter
import os
from modhostmanager import startModHost, connectToModHost, updateParameter, updateBypass, quitModHost, setUpPatch, setUpPlugins, varifyParameters, startJackdServer

class BoxWidget(QWidget):
    def __init__(self, indicator : int, plugin_name = "", bypass : int = 0):
        super().__init__()
        self.plugin_name = plugin_name
        self.indicator = indicator
        self.bypass = bypass
        self.setFixedSize(240, 801//3)
        self.initUI()
    
    def initUI(self):
        #Creating plugin name field
        self.label = QLabel(self.plugin_name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font : bold 30px;"
            "font-family : Comic Sans MS;"
        )
            # Adjust size after setting text
        self.label.adjustSize()
        self.label.move((self.width() - self.label.width()) // 2, self.height() // 2 - 20)

        # Indicator Label
        self.indicator = QLabel(str(self.indicator), self)
        self.indicator.setStyleSheet(
            "font: bold 30px;"
            "font-family : Comic Sans MS;"
            )
        
        # Move to bottom-left corner
        self.indicator.adjustSize()
        self.indicator.move(30-self.indicator.width(), self.height()-45)

        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.indicator_off_path = os.path.join(script_dir, "Graphics/IndicatorOff.png")
        self.indicator_on_path = os.path.join(script_dir, "Graphics/IndicatorOn.png")

        if(self.bypass == 0):
            indicator = QPixmap(self.indicator_on_path)
        else:
            indicator = QPixmap(self.indicator_off_path)
        

        self.indicator = QLabel(self)

        self.indicator.setPixmap(indicator)
        self.indicator.adjustSize()
        self.indicator.move((self.width() - self.indicator.width()) - 16, 16)

        if(self.bypass == 0):
            indicatorText = "On"
        else:
            indicatorText = "Off"

        

        self.indicator_text = QLabel(indicatorText, self)
        self.indicator_text.setStyleSheet(
            "font: bold 13px;"
            "font-family : Comic Sans MS;"
            )
        self.indicator_text.adjustSize()
        self.indicator_text.move((self.width() - self.indicator.width()) - 16, 16 + indicator.width())
    
    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)

    
    def updateBypass(self, bypass : int):
        self.bypass = bypass

        if(self.bypass == 1):
            indicator = QPixmap(self.indicator_off_path)
        else:
            indicator = QPixmap(self.indicator_on_path)

        self.indicator.setPixmap(indicator)
        self.indicator.adjustSize()
        self.indicator.move((self.width() - self.indicator.width()) - 16, 16)

        if(self.bypass == 0):
            indicatorText = "On"
        else:
            indicatorText = "Off"

        self.indicator_text.setText(indicatorText)
        self.indicator_text.adjustSize()
        self.indicator_text.move((self.width() - self.indicator.width()) - 16, 16 + indicator.width())

class BoxofPlugins(QWidget):
    def __init__(self,page : int, plugins : PluginManager):
        super().__init__()
        self.setFixedSize(480, 800)
        self.boxes = []
        for index in range(0, 3):
            try:
                plugin : Plugin = plugins.plugins[index + (3*(page))]
                box = BoxWidget(index + 3*page, plugin.name, plugin.bypass)
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)
            except Exception as e:
                box = BoxWidget(index + 3*page)
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)
        
    def updateBypass(self,page, position : int, bypass):
        try:
            self.boxes[position - (3*page)].updateBypass(bypass)
        except:
            pass

class Cursor(QWidget):
    def __init__(self, position : int = 0):
        super().__init__()
        self.position = position % 3
    
    def paintEvent(self, event):
        arrow_color = QColor("black")
        self.setFixedSize(480, 800) 

        painter = QPainter(self)
        x = 270
        y = 266
        width = 160
        arrowWidth = 30
        headOffset = 30
        adjusted_y = (y//2) + (y*self.position)
        

        #Line of arrow
        start = QPoint(x, adjusted_y)
        end = QPoint(x+width, adjusted_y)

        #Arrow head
        arrow_p1 = QPoint(x+headOffset+arrowWidth, adjusted_y + arrowWidth //2 )
        arrow_p2 = QPoint(x+headOffset+arrowWidth, adjusted_y - arrowWidth //2 )

        pen = QPen(arrow_color, 5)
        painter.setPen(pen)
        painter.drawLine(start, end)

        arrow_head = QPolygon([start, arrow_p1, arrow_p2])
        painter.setBrush(arrow_color)
        painter.drawPolygon(arrow_head)



    def changePointer(self,positon : int):
        self.position = positon
        self.update()

class ParameterReadingRange(QWidget):
    def __init__(self, parameter : Parameter):
        super().__init__()
        self.setFixedSize(240, 801//3)
        self.initUI(parameter)
    
    def initUI(self, parameter : Parameter):
        #Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font : bold 30px;"
            "font-family : Comic Sans MS;"
            "background : transparent;"
        )
        
        self.label.adjustSize()
        self.label.move((self.width() - self.label.width()) // 2, self.height() // 6)
        

        # Indicator Label
        self.value= QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(
            "font: bold 30px;"
            "font-family : Comic Sans MS;"
            )
        
        self.value.adjustSize()
        self.value.move((self.width() - self.value.width()) // 2, self.height() // 6 + self.label.height()  )

        #find path to Dial.png
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        image_path = os.path.join(script_dir, "Graphics/Dial.png")

        #Create Dial on screen
        self.dialImage = QPixmap(image_path) 
        self.dial = QLabel(self)
        #rotate Dial
        angle  = -140 + 280*(parameter.value)/(parameter.max-parameter.minimum)

        transformedPixelMap = self.dialImage.transformed(QTransform().rotate(angle))

        self.dial.setPixmap(transformedPixelMap)
        self.dial.adjustSize()
        self.dial.move((self.width() - transformedPixelMap.width()) // 2, self.height() // 6 + self.label.height() + self.value.height()+40 - (transformedPixelMap.height() // 2))

    def updateValue(self, parameter : Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move((self.width() - self.value.width()) // 2, self.height() // 6 + self.label.height())

        angle  = -140 + 280*(parameter.value)/(parameter.max-parameter.minimum)

        transformedPixelMap = self.dialImage.transformed(QTransform().rotate(angle))

        self.dial.setPixmap(transformedPixelMap)
        self.dial.adjustSize()
        self.dial.move((self.width() - transformedPixelMap.width()) // 2, self.height() // 6 + self.label.height() + self.value.height()+40 - (transformedPixelMap.height() // 2))

class ParameterReadingButton(QWidget):
    def __init__(self, parameter : Parameter):
        super().__init__()
        self.setFixedSize(240, 801//3)
        self.initUI(parameter)
    
    def initUI(self, parameter : Parameter):
        #Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font : bold 30px;"
            "font-family : Comic Sans MS;"
            "background : transparent;"
        )
        
        self.label.adjustSize()
        self.label.move((self.width() - self.label.width()) // 2, self.height() // 6)
        

        # Indicator Label
        self.value= QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(
            "font: bold 30px;"
            "font-family : Comic Sans MS;"
            )
        
        self.value.adjustSize()
        self.value.move((self.width() - self.value.width()) // 2, self.height() // 6 + self.label.height()  )

        #find path to Dial.png
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

        self.button_on_path = os.path.join(script_dir, "Graphics/BP.png")
        self.button_off_path = os.path.join(script_dir, "Graphics/BNP.png")

        
        #Create Dial on screen
        if(parameter.value == 0):
            button = QPixmap(self.button_off_path)
        else:
            button = QPixmap(self.button_on_path)
        

        self.button = QLabel(self)

        self.button.setPixmap(button)
        self.button.adjustSize()
        self.button.move((self.width() - self.button.width()) // 2, self.height() // 6 + self.label.height() + self.value.height()+15)
    
    def updateValue(self, parameter : Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move((self.width() - self.value.width()) // 2, self.height() // 6 + self.label.height())

        if(parameter.value == 0):
            button = QPixmap(self.button_off_path)
        else:
            button = QPixmap(self.button_on_path)
        
        self.button.setPixmap(button)
        self.button.adjustSize()
        self.button.move((self.width() - self.button.width()) // 2, self.height() // 6 + self.label.height() + self.value.height()+15)
   
class ParameterReadingSlider(QWidget):
    def __init__(self, parameter : Parameter):
        super().__init__()
        self.setFixedSize(240, 801//3)
        self.initUI(parameter)
    
    def initUI(self, parameter : Parameter):
        #Creating plugin name field
        self.label = QLabel(parameter.name, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font : bold 30px;"
            "font-family : Comic Sans MS;"
            "background : transparent;"
        )
        
        self.label.adjustSize()
        self.label.move((self.width() - self.label.width()) // 2, self.height() // 6)
        

        # Indicator Label
        self.value= QLabel(f"{parameter.value}", self)
        self.value.setStyleSheet(
            "font: bold 30px;"
            "font-family : Comic Sans MS;"
            )
        
        self.value.adjustSize()
        self.value.move((self.width() - self.value.width()) // 2, self.height() // 6 + self.label.height()  )

        #find path to Dial.png
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        slider = os.path.join(script_dir, "Graphics/Slider.png")
        
        sliderPix = QPixmap(slider)

        

        self.slider = QLabel(self)

        self.slider.setPixmap(sliderPix)
        self.slider.adjustSize()
        self.slider.move(((self.width() - self.slider.width()) // 2) - 40 + 80*(parameter.value// (parameter.max-parameter.minimum))
                         , self.height() // 6 + self.label.height() + self.value.height()+15)
    
    def paintEvent(self,event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        painter.drawLine(((self.width()) // 2)-40, self.height() // 6 + self.label.height() + self.value.height()+15 + self.slider.height()//2,
                         ((self.width()) // 2)+40, self.height() // 6 + self.label.height() + self.value.height()+15 + self.slider.height()//2)
    
    def updateValue(self, parameter : Parameter):
        self.value.setText(f"{parameter.value}")
        self.value.adjustSize()
        self.value.move((self.width() - self.value.width()) // 2, self.height() // 6 + self.label.height())

        self.slider.move(((self.width() - self.slider.width()) // 2) - 40 + 80*(parameter.value// (parameter.max-parameter.minimum))
                         , self.height() // 6 + self.label.height() + self.value.height()+15)
         
class ParameterPanel(QWidget):

    def __init__(self, background_color : str = "white", positon : int = 0, page : int = 0, plugin : Plugin = None):
        super().__init__()
        self.setFixedSize(480, 800)
        self.background_color = QColor(background_color)
        self.plugin = plugin
        self.position = positon
        self.page = page
        self.parameters = []
        self.initUI()

    def initUI(self):
         #Change to be done dynamically
        for index in range(0 , 3):
            try:
                parameter : Parameter = self.plugin.parameters[index + (self.page*3)]
                match parameter.mode:
                    case "dial":
                        dial = ParameterReadingRange(parameter)
                        dial.setParent(self)
                        dial.move(self.width()//2, (801//3) * index)
                        self.parameters.append(dial)

                    case "button":
                        button = ParameterReadingButton(parameter)
                        button.setParent(self)
                        button.move(self.width()//2, (801//3) * index)
                        self.parameters.append(button)
                    case "selector":
                        selector = ParameterReadingSlider(parameter)
                        selector.setParent(self)
                        selector.move(self.width()//2, (801//3) * index)
                        self.parameters.append(selector)
                    

            except:
                pass
    
    def updateParameter(self,position : int = 0):
        try:
            self.parameters[position].updateValue(self.plugin.parameters[position + (self.page * 3)])
        except:
            pass
        
    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(QColor(self.background_color), 10)
        painter.setPen(pen)

        rect = QRect((self.width()//2)-7, (self.height()//3)*self.position + 5, 15, self.height()//3-9)
        painter.fillRect(rect, self.background_color)

class BoardWindow(QWidget):
    def __init__(self, manager : PluginManager, mod_host_manager, restart_callback):
        super().__init__()
        self.plugins = manager
        self.mod_host_manager = mod_host_manager
        self.restart_callback = restart_callback
        self.backgroundColor = "#E2C290"

        self.rcount = 0

        self.mycursor = 0
        self.page = 0
        self.param_page = 0
        self.current = "plugins"


        self.setGeometry(0,0,480,800)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#E2C290"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.pluginbox = BoxofPlugins(self.page, self.plugins)
        self.pluginbox.setParent(self)

        self.arrow = Cursor(self.mycursor)
        self.arrow.setParent(self)
        self.arrow.raise_()

        self.pageNum = QLabel("Pgn " + str(self.page), self)
        self.pageNum.adjustSize()
        self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()

        match key:
            case Qt.Key_R:
                self.changeBypass(self.mycursor +(3* self.page))
            case Qt.Key_F:
                self.changeBypass(0)
            case Qt.Key_G:
                self.changeBypass(1)
            case Qt.Key_H:
                self.changeBypass(2)
            case Qt.Key_J:
                self.changeBypass(3)
            case Qt.Key_K:
                self.changeBypass(4)
            case Qt.Key_L:
                self.changeBypass(5)


        if key == Qt.Key_R:
            self.rcount += 1
            if self.rcount >= 6:
                quitModHost(self.mod_host_manager)
                self.restart_callback()
        else:
            self.rcount = 0

        match self.current:
            case "plugins":
                match key:
                    case Qt.Key_Q:
                        self.mycursor = max(0, self.mycursor - 1)
                        self.arrow.changePointer(self.mycursor)
                    
                    case Qt.Key_W:
                        self.openParamPage()
                        
                    case Qt.Key_E:
                        self.mycursor = min((2), self.mycursor + 1)
                        self.arrow.changePointer(self.mycursor)
                    
                    case Qt.Key_S:
                        self.pageUpPlugins()
                    
                    case Qt.Key_X:
                        self.pageDownPlugins() 
                    
                        

            case "parameters":
                match key:
                    case Qt.Key_Q:
                        self.descreaseParameter(0)
                        
                    case Qt.Key_W:
                        self.closeParamPage()
                    
                    case Qt.Key_E:
                        self.increaseParameter(0)
                    
                    case Qt.Key_A:
                        self.descreaseParameter(1)
                    
                    case Qt.Key_S:
                        self.pageUpParameters()
                    
                    case Qt.Key_D:
                        self.increaseParameter(1)
                    
                    case Qt.Key_Z:
                        self.descreaseParameter(2)

                    case Qt.Key_X:
                        self.pageDownParameters()
                    
                    case Qt.Key_C:
                        self.increaseParameter(2)                     
    
    def paintEvent(self, event):
        painter = QPainter(self)

        pen = QPen(Qt.black, 10)
        painter.setPen(pen)

        rect = QRect(0, 0, self.width()-1, self.height())
        painter.drawRect(rect)
    
    def showEvent(self,event):
        self.setFocus()

    def descreaseParameter(self, position : int):
        try:
            parameter : Parameter = self.plugin.parameters[position + 3*(self.param_page)]
            parameter.setValue(round(max(parameter.minimum, parameter.value - parameter.increment), 2))
            if updateParameter(self.mod_host_manager, self.mycursor + 3*self.page, parameter) != 0:
                print("Failed to update")
                pass
            self.paramPanel.updateParameter(position)
            self.update()
        except:
            pass

    def increaseParameter(self, position : int):
        try:
            parameter : Parameter = self.plugin.parameters[position + 3*(self.param_page)]
            parameter.setValue(round(min(parameter.max, parameter.value + parameter.increment), 2))
            if updateParameter(self.mod_host_manager, self.mycursor + 3*self.page, parameter) != 0:
                print("Failed to update")
                pass
            self.paramPanel.updateParameter(position)
            self.update()
        except:
            pass
    
    def openParamPage(self):
        try:
            self.param_page = 0
            self.plugin = self.plugins.plugins[self.mycursor + (3 * self.page)]
            self.paramPanel = ParameterPanel(self.backgroundColor, self.mycursor, self.param_page, self.plugin)
            self.paramPanel.setParent(self)
            self.paramPanel.show()
            self.arrow.hide()
            self.update()
            self.current = "parameters"

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()
                            
        except Exception as e:
            print(e)
            pass

    def closeParamPage(self):
        self.paramPanel.deleteLater()
        self.paramPanel.hide()
        self.paramPanel = None
        self.arrow.show()
        self.update()
        self.current = "plugins"
        self.plugin = None

        self.pageNum.setText("Pgn " + str(self.page))
        self.pageNum.adjustSize()
        self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
        self.update()
    
    def pageUpPlugins(self):
        if(self.page == 0):
            self.page = self.page + 1
            self.pluginbox.deleteLater()
            del self.pluginbox
            self.pluginbox = BoxofPlugins(self.page, self.plugins)
            self.pluginbox.setParent(self)
            self.pluginbox.show()

            self.pageNum.setText("Pgn " + str(self.page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()
    
    def pageDownPlugins(self):
        if(self.page == 1):
            self.page = self.page - 1
            self.pluginbox.deleteLater()
            del self.pluginbox
            self.pluginbox = BoxofPlugins(self.page, self.plugins)
            self.pluginbox.setParent(self)
            self.pluginbox.show()

            self.pageNum.setText("Pgn " + str(self.page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()

    def changeBypass(self, position):
        try:
            #get the value of bypass from the plugin our cursor is currently on
            plugin = self.plugins.plugins[position]
            bypass = plugin.bypass

            #flip value
            bypass = bypass ^ 1
            plugin.bypass = bypass
            updateBypass(self.mod_host_manager, position, plugin)
            self.pluginbox.updateBypass(self.page,position, bypass)
        except:
            pass
    
    def pageUpParameters(self):
        if(self.param_page == 0):
            self.param_page = self.param_page + 1
            self.paramPanel.deleteLater()
            del self.paramPanel
            self.paramPanel = ParameterPanel(self.backgroundColor, self.mycursor, self.param_page, self.plugin)
            self.paramPanel.setParent(self)
            self.paramPanel.show()

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()
    
    def pageDownParameters(self):
        if(self.param_page == 1):
            self.param_page = self.param_page - 1
            self.paramPanel.deleteLater()
            del self.paramPanel
            self.paramPanel = ParameterPanel(self.backgroundColor, self.mycursor, self.param_page, self.plugin)
            self.paramPanel.setParent(self)
            self.paramPanel.show()

            self.pageNum.setText("Pgn " + str(self.param_page))
            self.pageNum.adjustSize()
            self.pageNum.move(self.width()-self.pageNum.width()-25, self.height()-25)
            self.update()

class BoxofJsons(QWidget):
    def __init__(self,page : int, boards : list):
        super().__init__()
        self.setFixedSize(480, 800)
        self.boxes = []
        for index in range(0, 3):
            try:
                box = BoxWidget(index + 3*page, boards[index + 3*page])
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)
            except Exception as e:
                box = BoxWidget(index + 3*page)
                box.setParent(self)
                box.move(0, (self.height()//3)*index)
                self.boxes.append(box)

class PedalBoardSelectWindow(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.json_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_files = self.get_json_files(f"{self.json_dir}/Json")
        self.board = BoxofJsons(0, self.json_files)
        self.board.setParent(self)

        self.callback = callback

        self.mycursor = 0
        self.setGeometry(0,0,480,800)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#E2C290"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.arrow = Cursor(self.mycursor)
        self.arrow.setParent(self)
        self.arrow.raise_()

        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        key = event.key()
        
        match key:
            case Qt.Key_Q:
                self.mycursor = max(0, self.mycursor - 1)
                self.arrow.changePointer(self.mycursor)

            case Qt.Key_W:
                selected_file = os.path.join(f"{self.json_dir}/Json", self.json_files[self.mycursor])
                print(selected_file)
                self.callback(selected_file)
            
            case Qt.Key_E:
                self.mycursor = min(2, self.mycursor +1)
                self.arrow.changePointer(self.mycursor)
            
        

    def get_json_files(self,directory):
        """Returns a list of all JSON files in the specified directory."""
        return [f for f in os.listdir(directory) if f.endswith('.json')]

    def showEvent(self, event):
        self.setFocus()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 480, 800)

        self.stack = QStackedWidget(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stack)

        # Create selection screen
        self.start_screen = PedalBoardSelectWindow(self.launch_board)
        self.stack.addWidget(self.start_screen)

        self.board_window = None  # Placeholder for later

        self.show()

    def launch_board(self, selected_json):
        """Called when a JSON file is selected to load the board"""
        board = PluginManager()
        board.initFromJSON(selected_json)
        startModHost()
        modhost = connectToModHost()
        if modhost is None:
            print("Failed Closing...")
            return
        setUpPlugins(modhost, board)
        setUpPatch(modhost, board)
        varifyParameters(modhost, board)

        # Remove old board window if it exists
        if self.board_window is not None:
            self.stack.removeWidget(self.board_window)
            self.board_window.deleteLater()

        # Create new board window and add it to the stack
        self.board_window = BoardWindow(board, mod_host_manager=modhost, restart_callback=self.show_start_screen)
        self.stack.addWidget(self.board_window)
        self.stack.setCurrentWidget(self.board_window)  # Switch view
        self.board_window.setFocus()

    def show_start_screen(self):
        """Switch back to the start screen."""
        self.stack.setCurrentWidget(self.start_screen)  # Switch back
        self.start_screen.setFocus()


def main():
    app = QApplication(sys.argv)
    startJackdServer()
    time.sleep(.1)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

    

    

if __name__ == "__main__":
    main()

