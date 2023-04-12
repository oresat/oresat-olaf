from ...common.resource import Resource


class StoreEdsResource(Resource):
    '''
    Resource for the CANopen's standarize store EDS object that allow the master node to read the
    node's EDS file.
    '''

    def __init__(self, eds_path: str):
        super().__init__()

        self.index = 0x1021
        self.eds_path = eds_path

    def on_start(self):

        self.node.add_sdo_read_callback(self.index, self.on_read)

    def on_read(self, index: int, subindex: int) -> bytes:

        with open(self.eds_path, 'rb') as f:
            data = f.read()

        return data
