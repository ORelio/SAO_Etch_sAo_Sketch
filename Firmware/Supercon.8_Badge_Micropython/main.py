from machine import I2C, Pin
import time

enable_calib = True
enable_shaking = True

etch_right = None
etch_left = None

## do a quick spiral to test
if petal_bus:
    for j in range(8):
        which_leds = (1 << (j+1)) - 1 
        for i in range(1,9):
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
            time.sleep_ms(30)
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))

print("\n\n*****Boot done*****\n\n")

if etch_sao_sketch_device:
    etch_sao_sketch_device.shake() # clear display

    if enable_calib:
        # Calibrate after screen has started, to account for power drop caused by the OLED current draw
        print("Starting ADC calibration routine:")
        print("Within 5 seconds, in the following order")
        print("1. Turn both knobs all the way right")
        print("2. Turn both knobs all the way left")
        success = etch_sao_sketch_device.try_calibration_routine()
        if success:
            print("ADC calibration succeeded.")
            print(f"Calibration values: r={etch_sao_sketch_device.calib_right_zero_offset}, l={etch_sao_sketch_device.calib_left_zero_offset}, s={etch_sao_sketch_device.calib_voltage_scaling}")
        else:
            print("ADC calibration failed.")
            print(f"Using default values: r={etch_sao_sketch_device.calib_right_zero_offset}, l={etch_sao_sketch_device.calib_left_zero_offset}, s={etch_sao_sketch_device.calib_voltage_scaling}")

    time.sleep(1)
    etch_sao_sketch_device.shake()

while True:

    ## display button status on RGB
    if petal_bus:
        if not buttonA.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

        if not buttonB.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))

        if not buttonC.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))

    ## see what's going on with the touch wheel
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)

    ## display touchwheel on petal
    if petal_bus and touchwheel_bus:
        if tw > 0:
            tw = (128 - tw) % 256 
            petal = int(tw/32) + 1
        else: 
            petal = 999
        for i in range(1,9):
            if i == petal:
                petal_bus.writeto_mem(0, i, bytes([0x7F]))
            else:
                petal_bus.writeto_mem(0, i, bytes([0x00]))
    
    if etch_sao_sketch_device:
        # Check if the badge has been flipped, and clear the screen if it has
        if enable_shaking and etch_sao_sketch_device.shake_detected:
            print("Shake detected")
            etch_sao_sketch_device.shake()

        if etch_left is not None:
            prev_left = etch_left
        else:
            prev_left = None
        if etch_right is not None:
            prev_right = etch_right
        else:
            prev_right = None
        
        etch_left = etch_sao_sketch_device.left
        etch_right = 127 - etch_sao_sketch_device.right
        
        if prev_left is None:
            prev_left = etch_left
        if prev_right is None:
            prev_right = etch_right

        etch_sao_sketch_device.draw_line( prev_left, prev_right, etch_left, etch_right, 15)
        etch_sao_sketch_device.draw_display()
    
    bootLED.off()
