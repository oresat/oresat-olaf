'''Example App'''

from os.path import dirname, abspath
from argparse import ArgumentParser

from olaf import app_args_parser, parse_app_args, App

from .example_resource import ExampleResource

def main():
    # add the parent ArgumentParser for standard OreSat app args
    parser = ArgumentParser(parents=[app_args_parser])
    # add any other args here
    args = parser.parse_args()
    parse_app_args(args)  # parse the standard app args

    app = App(f'{dirname(abspath(__file__))}/example_app.dcf', args.bus, args.node_id)

    # Add the example resource
    app.add_resource(ExampleResource(app.node, app.fread_cache, app.work_base_dir + "/updater"))

    app.run()


if __name__ == '__main__':
    main()
