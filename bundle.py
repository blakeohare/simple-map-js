import os
import sys

def file_read_text(path):
    c = open(path.replace('/', os.sep), 'rt')
    t = c.read()
    c.close()
    return t.replace('\r\n', '\n')

def file_write_text(path, content):
    c = open(path.replace('/', os.sep), 'wb')
    c.write(content.replace('\r\n', '\n').encode('utf-8'))
    c.close()

def run_command(cmd):
    c = os.popen(cmd)
    output = c.read()
    c.close()
    return output

def main(args):

    js_code = '\n'.join([
        'const SimpleMap = (() => {',
        file_read_text('./src/util.js'),
        file_read_text('./src/dataloader.js'),
        file_read_text('./src/canvasmap.js'),
        file_read_text('./src/external.js'),
        'return Object.freeze({ loadData, create });',
        '})();',
        ''
    ])

    js_path = './dist/simplemap.js'
    file_write_text(js_path, js_code)

    js_code_minified = run_command('npx terser --compress --mangle -- ' + js_path)
    js_path_minified = js_path.replace('.js', '.min.js')
    file_write_text(js_path_minified, js_code_minified)

    print("Done.")

if __name__ == '__main__':
    main(sys.argv[1:])
