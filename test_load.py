import logging
import argparse

from ac_import import ACProject

def main():
	logging.basicConfig(level=logging.INFO)

	parser = argparse.ArgumentParser(description='Test loading of an AC project')
	parser.add_argument('path', nargs=1, help='Path to AC project to load')

	args = parser.parse_args()

	p = ACProject.load(args.path[0])

if __name__ == "__main__":
	main()
