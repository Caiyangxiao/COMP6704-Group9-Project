"""Combine the checked report and slide PDFs into the Canvas submission file.

The original portrait/landscape page sizes, searchable text, named destinations,
links and bookmarks are retained. No optimizer is run and no page is rasterized.
"""
from pathlib import Path
import argparse
import json
import logging
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT.parent


def annotation_count(reader):
    return sum(len(page['/Annots'].get_object()) if '/Annots' in page else 0 for page in reader.pages)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',default='../01_Report/Lasso_Project_Report.pdf')
    parser.add_argument('--slides',default='../04_Presentation/COMP6704_Group9_Lasso_Presentation.pdf')
    parser.add_argument('--output',default='../05_Submission/Group9.pdf')
    args=parser.parse_args()
    report=(ROOT/args.report).resolve();slides=(ROOT/args.slides).resolve();target=(ROOT/args.output).resolve()
    r=PdfReader(report);s=PdfReader(slides)
    if len(r.pages)>15:raise ValueError(f'Report exceeds the 15-page limit: {len(r.pages)}')
    target.parent.mkdir(parents=True,exist_ok=True)
    log=ROOT/'output/report_build/merge_warnings.log';log.parent.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(filename=log,filemode='w',level=logging.WARNING,encoding='utf-8')
    w=PdfWriter();w.append(report,outline_item='Project Report',import_outline=True)
    w.append(slides,import_outline=False)
    slides_bookmark=w.add_outline_item('Presentation Slides',len(r.pages))
    for label,number in [('Opening — ZHANG Kejia',1),('Part I — CAI Yangxiao',3),('Part II — XUE Pengyu',10),('Part III — ZHOU Xiyu',20),('Q&A — All four members',31),('Backup',32),('Selected references',34)]:
        if number<=len(s.pages):w.add_outline_item(label,len(r.pages)+number-1,parent=slides_bookmark)
    w.set_page_label(0,len(r.pages)-1,style='/D',start=1)
    w.set_page_label(len(r.pages),len(r.pages)+len(s.pages)-1,style='/D',prefix='Slide ',start=1)
    w.add_metadata({'/Title':'COMP6704 Group 9 — Lasso: Report and Presentation','/Author':'CAI Yangxiao; XUE Pengyu; ZHANG Kejia; ZHOU Xiyu','/Subject':'Four-solver comparison: ISTA, FISTA, cyclic CD, ADMM'})
    temp=target.with_suffix('.tmp.pdf');w.write(temp);w.close()
    c=PdfReader(temp)
    assert len(c.pages)==len(r.pages)+len(s.pages)
    for i,page in enumerate(list(r.pages)+list(s.pages)):
        assert c.pages[i].extract_text()==page.extract_text(),f'Text changed on page {i+1}'
        assert list(c.pages[i].mediabox)==list(page.mediabox),f'Page size changed on page {i+1}'
    assert annotation_count(c)==annotation_count(r)+annotation_count(s),'Links were lost during merge'
    assert set(r.named_destinations)<=set(c.named_destinations),'Report named destinations were lost'
    if temp.stat().st_size>=40_000_000:raise ValueError('Combined PDF is not smaller than 40 MB')
    temp.replace(target)
    summary={'report_pages':len(r.pages),'slide_pages':len(s.pages),'combined_pages':len(c.pages),'combined_bytes':target.stat().st_size,'text_and_page_sizes_match_sources':True,'all_annotations_preserved':True,'named_destinations_preserved':True,'report_page_limit_passed':True,'file_size_limit_passed':True}
    (target.parent/'submission_validation.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
