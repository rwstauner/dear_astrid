import sys
if sys.argv[0].endswith("__main__.py"):
  sys.argv[0] = "dear_astrid"

if __name__ == '__main__':
  from dear_astrid.main import main
  main()
