from pg.TCPBuffer import MessageType


def get_adapter(
        client,
        host_name,
        port,
        state_or_data=False,
        notify_small=False
):
    class Adapter(client):
        """
        notify_small
            if True; return everything when get_curr_data is passed without
            checking if new values are same as old

            sometimes value is passed as new value because there are not
            enough decimal places to check

            you can choose to ignore those values


        get_curr_state and get_curr_data can not work in tandem

        state_or_data
            True:
                get_curr_state works

            False:
                get_curr_data works

        """

        def __init__(
                self,
                host_name,
                port,
                state_or_data=True,
                notify_small=False,

        ):

            super().__init__(host_name, port)

            # todo add option to change, not sure if needed

            self.data = {}
            self.notify_small = notify_small
            self.is_init_called = False
            self._state_or_data = state_or_data
            # self.server_type = server_type

        async def _run(self):
            """
            driver for state memory

            :return:
            """

            if not self._state_or_data:
                raise Exception("this method can not be called in this mode,"
                                "switch on @state_or_data flag")

            t = await self.protocol.get_init_data()
            # self.data = dict(self.data, **{var_name: e.payload.data})
            # self.data = dict(self.data, t)
            self.data.update(t)

            print(self.data)

            while True:
                t = await self.protocol.get_curr_data()

                old = {k: v for k, v in self.data.items()}

                self.data.update(t)

                diff = set(old.items()) ^ set(self.data.items())
                print("diff", diff)

                # print(self.data)

        async def get_curr_state(self):
            """
            return current state of system
            include all values that were ever received

            :return:
            """

            if not self._state_or_data:
                raise Exception("this method can not be called in this mode,"
                                "switch on @state_or_data flag")

            await self.send(str(self.data))

            return self.data

        async def tcp_get_curr_data(self):
            # todo remove it and implement it in existing functions
            try:
                # return self.client.buffer.read_next()
                return self.receive()
            except IndexError:
                self.close()

        async def tcp_send_data(self, value, asdu=0, io=0,
                                data_type=MessageType.CONTENT):
            # todo remove it and implement it in existing functions
            self.send(value, data_type)

        async def get_init_data(self):
            """
            return only initial data of system

            :return:
            """

            # todo check if whole system state can be retrieved with interrogate
            if self.is_init_called:
                raise Exception("init already called")
            self.is_init_called = True

            # t = await self.protocol.get_init_data()
            # todo define 'init data' in TCP
            t = await self.get_curr_data()

            print(len(t))
            self.data.update(t)

            await self.send(str(t))

            return t

        async def get_curr_data(self):
            """
            catch one new state of system


            :return:
            """

            if self._state_or_data:
                raise Exception("this method can not be called in this mode,"
                                "switch off @state_or_data flag")

            if not self.is_init_called:
                raise Exception("init was not called")

            while True:

                # t = await self.protocol.get_curr_data()
                t = self.receive()

                if not self.notify_small:
                    for k, v in t.items():
                        if k in self.data:

                            if self.data[k] != v:
                                self.data.update(t)
                                await self.send(str(t))
                                return t

                        else:
                            self.data.update(t)
                            await self.send(str(t))
                            return t

                else:
                    self.data.update(t)
                    await self.send(str(t))
                    return t

        async def update_data(self):
            """
            asdu
            io
            payload

            try multiple times to update, add var for control
            this exist in some other script
            :return:
            """

            #         await self.send(t)
            raise NotImplementedError()

    return Adapter(host_name, port, state_or_data, notify_small)

# todo this client should be in runtime changable
