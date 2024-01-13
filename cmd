#!/usr/bin/env python

import click

from command.three_ma.main import backtest_three_ma


@click.group()
def main():
    pass


main.add_command(backtest_three_ma)

if __name__ == '__main__':
    main()
