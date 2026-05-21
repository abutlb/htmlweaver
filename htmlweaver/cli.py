import argparse
import sys
from .splitter import split_html
from .combiner import combine_html
from .exporters import export_vue, export_react

BANNER = """
🧵 htmlweaver — Split HTML into threads. Weave them back together.
"""


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        prog='htmlweaver',
        description='Split or combine HTML, CSS, and JavaScript files.'
    )
    subparsers = parser.add_subparsers(dest='command')

    # ── split ─────────────────────────────────────────────────
    split_parser = subparsers.add_parser(
        'split',
        help='Split an HTML file into separate HTML, CSS, and JS files.'
    )
    split_parser.add_argument(
        '--html', required=True,
        help='Path to the HTML file to split.'
    )
    split_parser.add_argument(
        '--output', default=None,
        help='Output directory (default: same as input file).'
    )

    # ── combine ───────────────────────────────────────────────
    combine_parser = subparsers.add_parser(
        'combine',
        help='Combine HTML, CSS, and JS files into a single HTML file.'
    )
    combine_parser.add_argument(
        '--html', required=True,
        help='Path to the HTML file.'
    )
    combine_parser.add_argument(
        '--css', default=None,
        help='Path to the CSS file.'
    )
    combine_parser.add_argument(
        '--js', default=None,
        help='Path to the JavaScript file.'
    )
    combine_parser.add_argument(
        '--output', default=None,
        help='Output file path (default: <name>_combined.html).'
    )

    # ── export command ────────────────────────────────────────
    export_parser = subparsers.add_parser(
        'export',
        help='Export HTML as a Vue or React component.'
    )
    export_parser.add_argument(
        '--html', required=True,
        help='Path to the HTML file to export.'
    )
    export_parser.add_argument(
        '--format', required=True,
        choices=['vue', 'react'],
        help='Target format: vue or react.'
    )
    export_parser.add_argument(
        '--output', default=None,
        help='Output directory (default: same as input file).'
    )


    # ── تنفيذ ─────────────────────────────────────────────────
    args = parser.parse_args()

    if args.command == 'split':
        result = split_html(args.html, args.output)
        if not result:
            sys.exit(1)

    elif args.command == 'combine':
        success = combine_html(args.html, args.css, args.js, args.output)
        if not success:
            sys.exit(1)
    # في قسم التنفيذ أضف هذا الـ elif
    elif args.command == 'export':
        if args.format == 'vue':
            result = export_vue(args.html, args.output)
        elif args.format == 'react':
            result = export_react(args.html, args.output)
        if not result:
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
