# Visual Debugging
These files provide some useful and hopefully easy to use tools to visualize what data you currently have. 

The debuggers are using pygame to open a new window and draw shapes onto it. Feel free to modify the debugger in 
order to suit your needs. 

Also Note that since pygame only kan have one window open at a time you are NOT able to run two different 
types of debuggers simultaneous.

## Getting started
In the example below you can see how you get started with the visual debugger. In this example a debugger for a heatmap is set as the debugger.

```python
from library import *
import numpy as np
import visualdebugger.heat_map_debugger
import visualdebugger.flow_debugger
import visualdebugger.path_debugger


class MyAgent(IDABot):
    def __init__(self):
        IDABot.__init__(self)

        self.debugging = True
        self.debugger = None
        if self.debugging:
            self.set_up_debugging()
    
    def set_up_debugging(self):
        self.debugger = visualdebugger.heat_map_debugger.HeatMapDebugger()
        self.debugger.set_color_map({(20, 20): (255, 255, 0)})
        self.debugger.set_update_frequency(0.5)

    def on_game_start(self):
        IDABot.on_game_start(self)
        self.debugger.on_start()

    def on_step(self):
        IDABot.on_step(self)
        if self.debugging:
            self.debugger.on_step(self.calculate_and_set_heatmap) # OBS function that is sent! NOT function call!

    def calculate_and_set_heatmap(self):
        my_units = self.get_my_units()
        heat = np.zeros((self.my_bot.map_tools.height, self.my_bot.map_tools.width))
        for unit in my_units:
            heat[int(unit.position.y)][int(unit.position.x)] = 20
        self.debugger.set_display_values(heat) # OBS important to set the values

```

1. You are probably best off having a boolean variable to make the switch between having the debugger on or off easy.

2. Initialize the type of visual debugger you want to use by calling the constructor for that class. In the example 
above this is done in the first line of “set_up_debugging()” and this function.

3. The debugger must set up a window in order to have somewhere to draw onto. This is done in its on_start(). A good 
place to call on this function is in on_game_start() just like in the example above.

4. In order to update what the debugger shows you call its on_step function. This function will only do things as 
often as the update frequency is set to (in the example above it is set to 0.5 Hz meaning once every other second). 
So you can call this in the agent on_step() just like in the example above. This on step function can also take another 
function and call on that function at that same frequency. It can be a good idea to have a function that calls the 
.set_display_values() and have that being called this way.

Note: The .set_display_values() takes different arguments based on what type of debugger you are using and if the 
values ain’t correctly formatted a print will occur and say so. Please continue reading this in order to see how to 
format the values or take a look directly in the source code.


## Structure
In this part you can see how to structure the parameters in order to show the values.

### All VisualDebuggers:
##### on_start(self)
Sets up a pygame window that the on_step will draw onto.

##### on_step(self, fun=None)
Will keep track of the time that the last update of the window occured and if it should update it will do so. And will 
also call on the function provided at the same time.

##### set_update_frequency(self, new_frequency)
Set how often you want the on_step to do things. The frequency is in Hertz (updates/second)

##### set_display_values(self, *args)
Set the values that should be displayed. The different types of debuggers have a bit different criterias for their 
arguments so please check below or check the source code to get a better understanding.

##### set_color_map(self, color_map)
The Heatmap and Path debuggers make it easy to have different colors being displayed based on value. Use this function 
to do so by inputting a color_map. The color_map should be a dictionary with tuples of length 2 as keys and length 3 
as values. The key is the interval of which the color should represent. The interval will include the first value and 
exclude the last value. And the three long tuples are (r, g, b) values. Note that if the colormap is not correctly 
formatted this call won't do anything and print that there was something wrong. Intervals are not allowed to overlap!

### FlowDebugger
##### .set_display_values(self, map_values)
map_values should be a 2d list or 2d numpy array where every row has the same length. The values have to be integers 
or floats between 0 and 2*pi. The values represent the angle in radians and when run, the window will display arrows 
pointing in those directions.

### HeatMapDebugger
##### .set_display_values(self, map_values)
map_values should be a 2d list or 2d numpy array where every row has the same length. The values have to be integers 
or floats. You are free to have these values represent whatever you want and based on the color_map you have set, the 
color of each square will have that color.

### PathDebugger
##### .set_display_values(self, relevant_coordinates, map_size=(152, 176))
This debugger can more or less do the exact same thing as the heatmap debugger but instead of having to provide an 
entire 2d array you just need to provide the specific coordinates as the relevant_coordinates parameter. This should 
be a dictionary with a tuple of coordinates (x, y) both integer values as key and the value you want that coordinate 
to have is the value in the dictionary. You can also provide the size of the map you want as a second tuple. This size 
defaults to (152, 176) since that is the size of the normal map used. But keep in mind that all the coordinates must 
be in the range of the map_size!

When using this debugger you can just like with the heatmap set the colormap in order to have different values for 
different coordinates display different colors.
