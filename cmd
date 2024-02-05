#!/usr/bin/env python

import click

from command.backtest.backtest1 import backtest1
from command.backtest.backtest2 import backtest2


@click.group()
def main():
    pass


main.add_command(backtest1)
main.add_command(backtest2)

if __name__ == '__main__':
    main()
