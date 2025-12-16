import tempfile
import shutil
import pathlib
from pathlib import Path
import logging 
import json
import subprocess

logging.basicConfig(level=logging.INFO ,filename="DocumentMaker.log" , filemode="w")

class WorkingDirectory:
    def __init__(self, keep_on_error=True , copy_out_to_dir: Path | None = None):
        self.keep_on_error = keep_on_error
        self.path: Path | None = None

        SCRIPT_DIR = Path(__file__).parent.resolve()
        TEMPLATE_DIR = SCRIPT_DIR / "templates"

        self.MarkdownTemplate = TEMPLATE_DIR / "template.md"
        self.TypstTemplate = TEMPLATE_DIR / "template.typ"

        self.data: Path | None = None
        self.generated: Path | None = None
        self.output: Path | None = None
        
        self.copy_out_to_dir = copy_out_to_dir
        
    def __enter__(self) -> "WorkingDirectory":
        self.path = Path(
            tempfile.mkdtemp(prefix="report-build-")
        )

        logging.info(f"Working directory created at: {self.path}")
        return self

    def __exit__(self, exc_type, exc, tb):
        logging.info(f"Cleaning up working directory: {self.path}")
        
        if exc_type is None:
            shutil.rmtree(self.path)
            return False

        if self.keep_on_error:
            logging.error(f"Preserving workdir due to error: {self.path}")
            return False

        shutil.rmtree(self.path)
        return False


def CreateDocuments(CleanedSentry: dict , output_dir: Path = None):
    with WorkingDirectory(keep_on_error=True , copy_out_to_dir=output_dir) as workdir:
        try: 
            data = workdir.path / 'data'
            generated = workdir.path / 'generated'
            output = workdir.path / 'output'
            
            data.mkdir()
            generated.mkdir()
            output.mkdir()
            
            workdir.data = data
            workdir.generated = generated
            workdir.output = output
            
            json.dump(CleanedSentry , open(workdir.data / 'sentry.json', 'w'))
            
            md = CreateMarkdown(workdir)
            typst = CreateTypst(workdir)
            
            
            with open(md, 'r') as f:
                logging.info("Generated Markdown Report:" + f.read().replace('\n', '    '))
            
            with open(typst, 'rb') as f:
                logging.info(f"Generated Typst Report: {typst} ({len(f.read())} bytes)")
            
            if workdir.copy_out_to_dir:        
                workdir.copy_out_to_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(md, workdir.copy_out_to_dir / 'report.md')
                shutil.copy(typst, workdir.copy_out_to_dir / 'report.pdf')

                return {
                    "markdown": workdir.copy_out_to_dir / 'report.md',
                    "typst": workdir.copy_out_to_dir / 'report.pdf'
                    # maybe add a metadata json too
                    }
            return None
        
        except Exception as e:
            logging.error(e.with_traceback(e.__getattribute__('__traceback__')))

def tryReplaceJinjaVarible(file , var_name , var_value):
    with open(file, 'r') as f:
        content = f.read()
        
    content = content.replace(f"{{{{ {var_name} }}}}" , str(var_value))
    
    with open(file, 'w') as f:
        f.write(content)
        
def CreateMarkdown(WorkDir: WorkingDirectory):
    report = WorkDir.generated / 'report.md'
    output_file = WorkDir.output / 'report.md'
    
    shutil.copy(WorkDir.MarkdownTemplate.as_posix() , report.as_posix())
    
    
    sentry_data = json.load(open(WorkDir.data / 'sentry.json', 'r'))
    dumpString = "hello markdown report\n```json\n"
    dumpString += json.dumps(sentry_data , indent=4)
    dumpString += "\n```\n"
    
    for key, value in sentry_data.items():
        tryReplaceJinjaVarible(report , key , value)
    tryReplaceJinjaVarible(report , "Dump" , dumpString)
    
    shutil.copy(report, output_file)
    
    return output_file

def CreateTypst(WorkDir: WorkingDirectory):
    typst_file = WorkDir.generated / 'report.typ'
    output_file = WorkDir.output / 'report.pdf'
    shutil.copy(WorkDir.TypstTemplate.as_posix(), typst_file.as_posix())
    shutil.copy(WorkDir.data / 'sentry.json', WorkDir.generated / 'sentry.json')
             
    cmd = ["typst", "compile", typst_file.as_posix() , output_file.as_posix()]
    subprocess.run(cmd, check=True)
    
    return output_file