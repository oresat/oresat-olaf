'''Example App'''

from os.path import dirname, abspath
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App


def main():
    # add the parent ArgumentParser for standard OreSat app args
    parser = ArgumentParser(parents=[app_args_parser])
    # add any other args here
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    app = App(f'{dirname(abspath(__file__))}/example_app.dcf', args.bus, args.node_id)

    # add resources as needed

    app.run()

    #functions that need examples (from olaf App class)

    #App.add_resource(resource: Resource)
    #Check with Ryan what this is expecting...

    #App.run() - does this need to be called?  looks like it broadcasts out from the OD

    #App.send_tpdo(tpdo: int) - this is a standard one-off message


if __name__ == '__main__':
    main()
