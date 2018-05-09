# gantry_control

# Contains files for gui control and hardware controller for Duro Lab gantry control


The program generates pulse trains for a two dimensional linear robot with stepper motor control. Paths are given in a modified gcode with these options:

1) Move in a horizontal direction at max speed

G0 X100 

2) Move in a vertical direction at max speed

G0 Y100

3) Move in a horizontal direction at a specified feed rate

G1 X100 F500

4) Move in a horizontal direction at a specified feed rate

G1 Y100 F500

5) Move in a sinusoidal motion with constant feed rate, amplitude and period

G83 A100 T100 F500 N1

All distances are in mm, and feed rates are in mm/min
