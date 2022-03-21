import time
import asyncio
import concurrent.futures
import numpy as np
from pcaspy import SimpleServer, Driver


def create_quad_pv(name, server):
    tokens = name.split(':')
    prefix = ':'.join(tokens[:-1]) + ':'

    pvdb = {
        prefix + 'STATCTRLSUB.T': {
            'value': 1,
            # 'scan': 0.1,
        },
        prefix + 'BACT': {
            'value': 0,
            # 'scan': 0.1,
            'prec': 3,
        },
        prefix + 'BCTRL': {
            'value': 0,
            'prec': 3,
        },
        prefix + 'BCTRL.DRVL': {
            'value': -10,
            'prec': 3,
        },
        prefix + 'BCTRL.DRVH': {
            'value': 10,
            'prec': 3,
        },
    }

    server.createPV('', pvdb)


def create_pv(name, server):
    pvdb = {}
    pvdb[name] = {
        'value': 0,
        # 'scan': 0.1,
        'prec': 3,
    }

    server.createPV('', pvdb)


class myDriver(Driver):
    def __init__(self):
        super(myDriver, self).__init__()

    async def ramp_up(self, readout, flag, curr, dest, rate=0.1):
        self.setParam(flag, 1)
        self.updatePVs()

        n = int(np.ceil(np.abs(dest - curr) / rate))
        steps = np.linspace(curr, dest, n)
        for step in steps:
            await asyncio.sleep(rate)
            self.setParam(readout, step)

            q1 = self.getParam('QUAD:IN20:121:BACT')
            q2 = self.getParam('QUAD:IN20:122:BACT')
            q3 = self.getParam('QUAD:IN20:371:BACT')
            q4 = self.getParam('QUAD:IN20:361:BACT')
            obj = np.linalg.norm([q1, q2, q3, q4])
            self.setParam('SIOC:SYS0:ML00:CALC252', obj)

            self.updatePVs()

        self.setParam(flag, 0)
        self.updatePVs()

    def write(self, reason, value):
        if reason.startswith('SOLN') or reason.startswith('QUAD'):
            self.setParam(reason, value)
            tokens = reason.split(':')
            if tokens[-1] == 'BCTRL':
                flag = ':'.join(tokens[:-1] + ['STATCTRLSUB.T'])
                readout = ':'.join(tokens[:-1] + ['BACT'])
                curr = self.getParam(readout)
                # self.setParam(flag, 1)

                pool = concurrent.futures.ThreadPoolExecutor()
                pool.submit(asyncio.run, self.ramp_up(readout, flag, curr, value))
                # loop = asyncio.get_event_loop()
                # loop.run_until_complete(self.ramp_up(readout, flag, curr, value))
                # asyncio.create_task(self.ramp_up(readout, flag, curr, value))
                # task = loop.create_task(self.ramp_up(readout, flag, curr, value))
                # print(task)
                # _thread.start_new_thread(self.ramp_up, (readout, flag, curr, value))
        else:
            self.setParam(reason, value)

        return True


if __name__ == '__main__':
    pv_list = [
        'MTEST:RAND',
        'SOLN:IN20:121:BCTRL',  # solenoid
        'QUAD:IN20:121:BCTRL',  # skew quad
        'QUAD:IN20:122:BCTRL',  # skew qaud
        'QUAD:IN20:371:BCTRL',  # Q371
        'QUAD:IN20:361:BCTRL',  # Q361
        'SIOC:SYS0:ML00:CALC252',  # target
    ]

    server = SimpleServer()
    for pv in pv_list:
        if pv.startswith('SOLN') or pv.startswith('QUAD'):
            create_quad_pv(pv, server)
        else:
            create_pv(pv, server)
    driver = myDriver()
    print('Now serving...')
    while True:
        # process CA transactions
        server.process(0.1)
