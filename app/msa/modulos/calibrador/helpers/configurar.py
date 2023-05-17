from os import popen


class XInput(object):
    @staticmethod
    def get_device_with_prop(prop, id_only=True):
        devices = []
        proc = popen('xinput list --id-only')
        stdout = proc.read()
        dev_ids = stdout.split('\n')[0:-1]

        # Searching Virtual core keboard.
        idx = dev_ids.index('3')
        dev_ids = dev_ids[:idx]
        if not id_only:
            proc = popen('xinput list --name-only')
            stdout = proc.read()
            dev_names = stdout.split('\n')[0:-1]

        for i, id in enumerate(dev_ids):
            proc = popen('xinput list-props %s' % id)
            stdout = proc.read()
            if prop in stdout:
                stdout = stdout.split('\n')
                for property in stdout:
                    if prop in property:
                        if '<no items>' not in property:
                            setted = False
                        else:
                            setted = True

                        if id_only:
                            devices.append((id, setted))
                        else:
                            devices.append((dev_names[i], id, setted))
        return devices

    @staticmethod
    def get_prop(dev_id, prop):
        value = None
        proc = popen('xinput list-props  %s' % dev_id)
        stdout = proc.read()
        if prop in stdout:
            stdout = stdout.split('\n')
            for property in stdout:
                if prop in property:
                    value = property.split(':')[1]
                    value = value.replace('\t', '')
                    value = value.split(',')
                    break
        return value

    @staticmethod
    def get_prop_range(dev_id):
        value = []
        proc = popen('xinput list --long  %s' % dev_id)
        stdout = proc.read()
        stdout = stdout.split('\n')
        for line in stdout:
            if 'Range' in line:
                str_range = line.split(':')[1]
                str_range = str_range.replace(' ', '')
                axis_range = str_range.split('-')
                value += axis_range
        return value[:4]

    @staticmethod
    def set_prop(dev_id, property, data):
        command = 'xinput set-prop {0} {1} {2}'.format(dev_id, property, data)
        # escribo en un script temporal todos los comandos de calibración realizados
        # para que si se resetea el hub usb se puedan ejecutar de nuevo meidante
        # una regla udev que se configura aparte para ejecutar ese script.
        with open('/tmp/touch-calibration.sh', 'a') as fp:
            fp.write(command + '\n')
        popen(command)

    @staticmethod
    def get_dev_vendor(dev_id):
        cmd = 'xinput list-props {} | grep "Device Node" | cut -d ":" -f 2'.\
            format(dev_id)
        proc = popen(cmd)
        stdout = proc.read().strip()
        stdout = stdout.replace('\"', '')
        event = stdout.split('/')[-1]

        cmd = 'grep -E "Handlers|Bus=" /proc/bus/input/devices | grep -B1 ' \
              '"{}" | head -n 1 | cut -d ":" -f 2'.format(event)
        proc = popen(cmd)
        stdout = proc.read().strip()
        dev = stdout.split()
        dev = [d.split('=')[1] for d in dev]
        dev = {'bus': dev[0],
               'vendor': dev[1],
               'product': dev[2],
               'version': dev[3]}

        return dev


class XInputCalibrationMatrix:
    """
    Being 'Si' a matrix containing 3 pairs of points ((sx₁, sy₁), (sx₂, sy₂),
    (sx₃, sy₃)) corresponding to the screen, and 'Ti' a matrix containing 3
    pairs of points corresponding to the touchscreen, it is possible to define
    a calibration matrix 'C' such that 'C * Ti = Si'. Indeed, the values of 'C'
    can be computed as 'C = Si * inv(Ti)'.

    More specifically:

          ⎡tx₁  tx₂  tx₃⎤
          ⎢             ⎥
    Ti =  ⎢ty₁  ty₂  ty₃⎥
          ⎢             ⎥
          ⎣ 0    0    1 ⎦

          ⎡sx₁  sx₂  sx₃⎤
          ⎢             ⎥
    Si =  ⎢sy₁  sy₂  sy₃⎥
          ⎢             ⎥
          ⎣ 0    0    1 ⎦

          ⎡a  b  c⎤
          ⎢       ⎥
    C =   ⎢d  e  f⎥
          ⎢       ⎥
          ⎣0  0  1⎦

    Then:
    ⎡a  b  c⎤     ⎡tx₁  tx₂  tx₃⎤    ⎡sx₁  sx₂  sx₃⎤
    ⎢       ⎥     ⎢             ⎥    ⎢             ⎥
    ⎢d  e  f⎥  x  ⎢ty₁  ty₂  ty₃⎥ =  ⎢sy₁  sy₂  sy₃⎥
    ⎢       ⎥     ⎢             ⎥    ⎢             ⎥
    ⎣0  0  1⎦     ⎣ 0    0    1 ⎦    ⎣ 0    0    1 ⎦

    For more information, refer to:
    https://askubuntu.com/questions/1275038/coordinate-transformation-matrix-and-libinput-calibration-matrix-how-are-t
    https://github.com/kreijack/xlibinput_calibrator/blob/master/src/calibrator.cc#L144
    """
    def mat9_product_simple(c, m1):
        for i in range(9):
            m1[i] *= c
        return m1

    def mat9_product(m1, m2):
        m3 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(3):
            for j in range(3):
                sum = 0
                for k in range(3):
                    sum += m1[i*3+k]*m2[j+k*3]
                m3[i*3+j] = sum
        return m3

    def mat9_invert(m):
        m4857 = m[4] * m[8] - m[5] * m[7]
        m3746 = m[3] * m[7] - m[4] * m[6]
        m5638 = m[5] * m[6] - m[3] * m[8]
        det = m[0] * (m4857) + m[1] * (m5638) + m[2] * (m3746)

        invdet = 1 / det
        minv = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # Matrix33d minv; // inverse of matrix m
        minv[0] = (m4857) * invdet
        minv[1] = (m[2] * m[7] - m[1] * m[8]) * invdet
        minv[2] = (m[1] * m[5] - m[2] * m[4]) * invdet
        minv[3] = (m5638) * invdet
        minv[4] = (m[0] * m[8] - m[2] * m[6]) * invdet
        minv[5] = (m[2] * m[3] - m[0] * m[5]) * invdet
        minv[6] = (m3746) * invdet
        minv[7] = (m[1] * m[6] - m[0] * m[7]) * invdet
        minv[8] = (m[0] * m[4] - m[1] * m[3]) * invdet
        return minv

    def mat9_sum(m1, m2):
        for i in range(9):
            m2[i] += m1[i]
        return m2

    def compute(num_blocks, width, height, clicks):
        # clicks= {'tl':[1021,116],
        #        'tr':[1046,648],
        #        'br':[216,645],
        #        'bl':[220,110]}
        # num_blocks = 8
        # width = 1366
        # height = 768
        xl = width / num_blocks
        xr = width / num_blocks * (num_blocks - 1)
        yu = height / num_blocks
        yl = height / num_blocks * (num_blocks - 1)

        # skip LR
        tm = [clicks['tl'][0],   clicks['tr'][0],  clicks['bl'][0],
              clicks['tl'][1],   clicks['tr'][1],  clicks['bl'][1],
              1,                 1,                1]
        ts = [xl, xr, xl,
              yu, yu, yl,
              1,  1,  1]

        tmi = XInputCalibrationMatrix.mat9_invert(tm)
        coeff = XInputCalibrationMatrix.mat9_product(ts, tmi)

        # skip UL
        tm = [clicks['br'][0],   clicks['tr'][0],  clicks['bl'][0],
              clicks['br'][1],   clicks['tr'][1],  clicks['bl'][1],
              1,                 1,                1]
        ts = [xr,              xr,             xl,
              yl,              yu,             yl,
              1,               1,              1]
        tmi = XInputCalibrationMatrix.mat9_invert(tm)
        coeff_tmp = XInputCalibrationMatrix.mat9_product(ts, tmi)
        coeff = XInputCalibrationMatrix.mat9_sum(coeff, coeff_tmp)

        # skip UR
        tm = [clicks['br'][0],   clicks['tl'][0],  clicks['bl'][0],
              clicks['br'][1],   clicks['tl'][1],  clicks['bl'][1],
              1,                 1,                1]
        ts = [xr,              xl,             xl,
              yl,              yu,             yl,
              1,               1,              1]
        tmi = XInputCalibrationMatrix.mat9_invert(tm)
        coeff_tmp = XInputCalibrationMatrix.mat9_product(ts, tmi)
        coeff = XInputCalibrationMatrix.mat9_sum(coeff, coeff_tmp)

        # skip LL
        tm = [clicks['br'][0],   clicks['tl'][0],  clicks['tr'][0],
              clicks['br'][1],   clicks['tl'][1],  clicks['tr'][1],
              1,                 1,                1]
        ts = [xr,              xl,             xr,
              yl,              yu,             yu,
              1,               1,              1]
        tmi = XInputCalibrationMatrix.mat9_invert(tm)
        coeff_tmp = XInputCalibrationMatrix.mat9_product(ts, tmi)
        coeff = XInputCalibrationMatrix.mat9_sum(coeff, coeff_tmp)
        coeff = XInputCalibrationMatrix.mat9_product_simple(1.0/4.0, coeff)
        coeff[1] *= height/width
        coeff[2] *= 1.0/width

        coeff[3] *= width/height
        coeff[5] *= 1.0/height

        coeff[6] = 0
        coeff[7] = 0
        coeff[8] = 1

        print("{:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f} {:.7f}".format(
            coeff[0], coeff[1], coeff[2],
            coeff[3], coeff[4], coeff[5],
            coeff[6], coeff[7], coeff[8]
        ))

        return coeff