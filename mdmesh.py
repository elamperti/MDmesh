#!/usr/bin/env python

import sys
import os
import argparse
import re

import markdown2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple tool to merge many MarkDown files into one.')

    parser.add_argument('-n', '--no-separators', dest='use_separators', action='store_false', 
                        help='Merges documents without a separator between them.')
    
    #parser.add_argument('-f', '--follow-links', dest='follow_links', action='store_true',
    #                    help='Attach linked MarkDown documents to the queue.')
    
    parser.add_argument('-q', '--html-only', dest='create_md', action='store_false',
                        help='Outputs only an HTML with the merged documents.')
    
    parser.add_argument('-m', '--md-only', dest='create_html', action='store_false',
                        help='Outputs only a MarkDown file with the merged documents.')
    
    parser.add_argument('-p', '--plain', dest='use_template', action='store_false',
                        help='Plain HTML output, without template.')                    

    parser.add_argument('-o', '--output', metavar='filename', dest='output', type=str, default="output")    

    parser.add_argument('-c', metavar='style.css', dest='css', type=str, default="github-markdown-css/github-markdown.css",
                        help='Custom stylesheet path')

    parser.add_argument('-t', '--title', metavar='"Document title"', dest='title', type=str, default="Document")

    parser.add_argument('files', metavar='file', type=file, nargs='+',
                        help='MarkDown files to merge.')

    args = parser.parse_args()

    md_mesh = ""
    for md_file in args.files:
        if args.use_separators and md_mesh:
            md_mesh += "\n\n---\n\n"

        md_mesh += md_file.read()
        md_file.close()

    args.output = re.sub(r'\.(md|html)$', '', args.output, flags=re.IGNORECASE)
    md_path = args.output + '.md'
    html_path = args.output + '.html'

    if args.create_md:
        md_output = open(md_path, 'w')
        md_output.write(md_mesh)
        md_output.close()

    if args.create_html:
        raw_html = markdown2.markdown(md_mesh, extras=['tables', 'fenced-code-blocks'])
        html_output = open(html_path, 'w')

        if args.use_template:
            t = open('template.html', 'r')
            template = t.read()
            t.close()

            template = template.replace('{{ title }}', args.title)
            if args.css:
                try: 
                    css_file = open(args.css, 'r')
                    css = css_file.read()
                    css_file.close()
                except:
                    css = ""
                template = template.replace('{{ css }}', css)
            template = template.replace('{{ content }}', raw_html)

            html_output.write(template)

        else:
            html_output.write(raw_html)

        html_output.close()
