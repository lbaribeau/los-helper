
from matplotlib import pyplot
import math

# From my thesis!

def do_ticks_current_figure(): 
    do_y_ticks_current_figure() 
    do_x_ticks_current_figure() 
 
def do_y_ticks_current_figure(): 
    do_y_ticks( 
        min([min(L.get_ydata()) for L in pyplot.gca().get_lines()]), 
        max([max(L.get_ydata()) for L in pyplot.gca().get_lines()])) 
def do_x_ticks_current_figure(): 
    do_x_ticks( 
        min([min(L.get_xdata()) for L in pyplot.gca().get_lines()]), 
        max([max(L.get_xdata()) for L in pyplot.gca().get_lines()])) 
 
def do_y_ticks(ymin,ymax): 
    do_ticks(ymin,ymax,pyplot.gca().set_yticks, pyplot.gca().set_ylim) 
def do_x_ticks(xmin,xmax): 
    do_ticks(xmin,xmax,pyplot.gca().set_xticks, pyplot.gca().set_xlim)  
 
def do_ticks(amin, amax, set_tick_function, set_limits_function, amount=''): 
    print('do_ticks doing range %f to %f' % (amin,amax))  # "a" is a standin for either x or y
    _range=amax-amin
    try: 
        if amount=='more':
            order = math.floor(math.log10(amax-amin)) 
        elif amount=='less':
            order = math.ceil(math.log10(amax-amin)) 
        else: 
            order = round(math.log10(amax-amin)) 
    except ValueError as e: 
        print("do_ticks() failed, returning, maybe range too small, error printed:") 
        print(str(e)) 
        return 
    major_step   = pow(10,order-1) 
    minor_step   = pow(10,order-2) 
    bottom       = math.floor(amin/major_step)*major_step 
    bottom_minor = math.floor(amin/minor_step)*minor_step 
    set_tick_function( 
        [r*major_step+bottom for r in range(0,math.ceil((amax-amin)/major_step)+1)])  
    set_tick_function( 
        [r*minor_step+bottom_minor for r in range(0,math.ceil((amax-amin)/minor_step)+1)], 
        minor=True)  
    set_limits_function(amin-.1*_range,amax+.1*_range) 
 
def do_grid(): 
    pyplot.grid(which='minor',color='#dddddd', zorder=0) 
    pyplot.grid(which='major',color='#cccccc', zorder=0)
    pyplot.gca().set_axisbelow(True)

def auto_config():
	do_ticks_current_figure()
	do_grid()
	pyplot.tight_layout()
	# pyplot.show()

# def auto_config_hist():
# 	do_ticks_current_figure()
# 	do_grid()
# 	pyplot.tight_layout()

def show():
	pyplot.show()

# def plot_data(d):
# 	pyplot.plot(d)
# 	config_plot()

def get_pyplot():
	return pyplot
