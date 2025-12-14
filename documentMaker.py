import tempfile
import shutil
import pathlib
from pathlib import Path
import logging 
import json
import subprocess

logging.basicConfig(level=logging.INFO)

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
        return True
        if exc_type is None:
            shutil.rmtree(self.path)
            return False

        if self.keep_on_error:
            logging.error(f"Preserving workdir due to error: {self.path}")
            return False

        shutil.rmtree(self.path)
        return False


def CreateDocuments(CleanedSentry: dict):
    with WorkingDirectory(keep_on_error=True , copy_out_to_dir=Path.cwd() / 'exported') as workdir:
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
            
            json.dump(CleanedSentry , open(data / 'sentry.json', 'w'))
            
            md = CreateMarkdown(workdir)
            typst = CreateTypst(workdir)
            
            
            with open(md, 'r') as f:
                logging.info("Generated Markdown Report:\n" + f.read())
            
            with open(typst, 'rb') as f:
                logging.info(f"Generated Typst Report: {typst} ({len(f.read())} bytes)")
            
            if workdir.copy_out_to_dir:        
                workdir.copy_out_to_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy(md, workdir.copy_out_to_dir / 'report.md')
                shutil.copy(typst, workdir.copy_out_to_dir / 'report.pdf')
            
        except Exception as e:
            print(e.with_traceback(e.__getattribute__('__traceback__')))

def CreateMarkdown(WorkDir: WorkingDirectory):
    report = WorkDir.generated / 'report.md'
    output_file = WorkDir.output / 'report.md'
    
    shutil.copy(WorkDir.MarkdownTemplate.as_posix() , report.as_posix())
    
    
    sentry_data = json.load(open(WorkDir.data / 'sentry.json', 'r'))
    with open (report , 'a') as file:
        # replace the jinja style variables with sentry data
        #TODO put the jinja templates in the template file
        
        file.write("hello markdown report\n")
        file.write("```json\n")
        file.write(json.dumps(sentry_data , indent=4))
        file.write("\n```\n")
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