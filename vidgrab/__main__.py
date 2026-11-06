from .cli import main
import sys
sys.exit(main(sys.argv[1:] or ["web"]))
