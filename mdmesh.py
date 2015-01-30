#!/usr/bin/env python

import sys
import os
import argparse
import re

import markdown2


class FileQueue(object):
    def __init__(self):
        self.queue = [] # [path, pointer]
        self.last_used = 0

    def add(self, file_path, file_pointer=None):
        for item in self.queue:
            if item[0] == file_path:
                print (file_path + " ALREADY EXISTS")
                return # Already on queue

        if not file_pointer:
            try: 
                file_pointer = open(file_path, 'r')
            except: #FIXME
                print("Reference not found: " + path)

        self.queue.append([file_path, file_pointer])

    def get(self):
        if self.has_items:
            next_item = self.queue[self.last_used]
            self.last_used += 1
            return next_item
        else:
            return None

    def has_items(self):
        return self.last_used < len(self.queue)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple tool to merge many MarkDown files into one.')

    parser.add_argument('-n', '--no-separators', dest='use_separators', action='store_false', 
                        help='Merges documents without a separator between them.')
    
    parser.add_argument('-f', '--follow-links', dest='follow_links', action='store_true',
                        help='Attach linked MarkDown documents to the queue.')
    
    parser.add_argument('-q', '--html-only', dest='create_md', action='store_false',
                        help='Outputs only an HTML with the merged documents.')
    
    parser.add_argument('-m', '--md-only', dest='create_html', action='store_false',
                        help='Outputs only a MarkDown file with the merged documents.')
    
    parser.add_argument('-p', '--plain', dest='use_template', action='store_false',
                        help='Plain HTML output, without template.')                    

    parser.add_argument('-o', '--output', metavar='filename', dest='output', type=str, default="output")    

    parser.add_argument('-c', metavar='style.css', dest='css', type=str, 
                        default="github-markdown-css/github-markdown.css",
                        help='Custom stylesheet path')

    parser.add_argument('-t', '--title', metavar='"Document title"', dest='title', type=str, default="Document")

    parser.add_argument('files', metavar='file', type=file, nargs='+',
                        help='MarkDown file(s) to merge.')

    args = parser.parse_args()

    if args.follow_links:
        inline_links = re.compile(r'(?<=\]\().+\.md(?=\))', re.MULTILINE)  # 

    file_queue = FileQueue()
    for file_pointer in args.files:
        full_path = os.path.abspath(file_pointer.name)
        file_queue.add(full_path, file_pointer)

    md_mesh = ""
    while file_queue.has_items():
        (path, md_file) = file_queue.get()
        print ("READING " + path)
        if args.use_separators and md_mesh:
            md_mesh += "\n\n---\n\n"

        if not md_file:
            # If the file was found following links there's no file pointer yet
            try:
                md_file = open(path, 'r')
            except: # FIXME
                print("Reference not found: " + path)

        new_file = md_file.read()
        md_file.close()

        if args.follow_links:
            links = inline_links.findall(new_file)
            if links:
                base_path = os.path.dirname(os.path.abspath(md_file.name))
                for link in links:
                    file_queue.add(base_path + '/' + link)

        md_mesh += new_file

    args.output = re.sub(r'\.(md|html)$', '', args.output, flags=re.IGNORECASE)
    md_path = args.output + '.md'
    html_path = args.output + '.html'

    if args.create_md:
        md_output = open(md_path, 'w')
        print (os.path.abspath(md_output.name))
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