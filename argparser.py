#!/usr/bin/env python
import argparse
import commands
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="nsds")
    parser.add_argument('--env', action="store",required=True)
    return parser.parse_args()

def test1(env):
    print env


if __name__ == '__main__':
    args = parse_args()
    test1(args.env)
   

