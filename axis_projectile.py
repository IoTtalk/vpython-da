from visual import *

axis = []
labels = []
axis_label = 1

def init():
    a = 0
    b = 0
    c = 500
    d = 200
    axis.append(arrow(pos=(a,b,0), axis=(c+50,0,0), shaftwidth= 1, color = color.white))
    axis.append(arrow(pos=(a,b,0), axis=(0,d+50,0), shaftwidth= 1, color = color.white))
    
    #y1 = box(pos=(-198,-130,0), length=4, height=1, width=1)
    
    for t in range(0,20):
        #box(pos=(-100 + a*100,-128,0), length=1, height=2, width=1)
        axis.append(box(pos=(a + (t+1)*(c/20),b+d/2,0), length=1, height=d, width=1))
    
    for j in range(0,10):
        #for i in range(0,40):
            #box(pos=(-188 + i*10,-115 + j*15,-2), length=2, height=1, width=1,color=color.gray(0.8))
        axis.append(box(pos=(a + c/2,b + (j+1)*(d/10),0), length=c, height=1, width=1,color=color.gray(0.8)))
    
    for x in range(0,6):
        num = str(x*(c/5))
        #label(pos=(-200 + x*100,-145,0), text = num, height = 20, border = 12, font = 'monospace', color = color.black, box = False)
        labels.append(label(pos=(a + x*(c/5),b-2*d/20,0), text = num, height = 20, border = 12, font = 'monospace', color = color.white, box = False))
    
    for y in range(0,6):
        num = str(b+y*(d/5))
        #label(pos=(-220,-130 + y*30,0), text = num, height = 20, border = 12, font = 'monospace', color = color.black, box = False)
        labels.append(label(pos=(a-2*c/40,b + y*(d/5),0), text = num, height = 20, border = 12, font = 'monospace', color = color.white, box = False))
        
def hide():
    global axis,labels
    #print 2
    for g in axis:
        g.visible = False
    for h in labels:
        h.visible = False

def show_axis(key):
    if key == 'a':
        init()
        
def hide_axis(key):
    if key == 'a':
        hide()
        
def keyInput(evt):
    s = evt.key
    global axis_label
    if s == 'a' and axis_label == 1:
        show_axis(s)
        axis_label = 0
        print 1
    elif s == 'a' and axis_label == 0:
        hide_axis(s)
        axis_label = 1
        #print 1
