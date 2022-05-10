'''Example App'''

from os.path import dirname, abspath
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

from .example_resource import ExampleResource

def main():
    # where can we find a list of these args?
    # add the parent ArgumentParser for standard OreSat app args
    parser = ArgumentParser(parents=[app_args_parser])
    # add any other args here
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    app = App(f'{dirname(abspath(__file__))}/example_app.dcf', args.bus, args.node_id)

    # add resources as needed

    app.add_resource(ExampleResource(app.node, app.fread_cache, app.work_base_dir + "/updater"))

    app.run()



    #functions that need examples (from olaf App class)

    #App.add_resource(resource: Resource)
    #Check with Ryan what this is expecting...

    #App.run() - does this need to be called?  looks like it broadcasts out from the OD

    #App.send_tpdo(tpdo: int) - this is a standard one-off message

    #are there other functions that we need to look for?


if __name__ == '__main__':
    main()
