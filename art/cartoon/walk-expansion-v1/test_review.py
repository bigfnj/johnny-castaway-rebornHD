"""Exercise the generated page in Chromium and isolate input/render mutations.

Requires --exports, --original-native and --output. The real page is never
modified. Browser-source mutants are separate local pages with a verified
loaded-script digest and a pixel or timing execution witness.
"""
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()

def build(script,exports,native,output):
 r=subprocess.run([sys.executable,"-B",str(script),"--exports",str(exports),"--original-native",str(native),"--output",str(output)],capture_output=True,text=True)
 assert "WITNESS review.py SHA256="+sha(script.read_bytes()) in r.stdout,"review.py execution witness"
 return r

def open_page(browser,path):
 page=browser.new_page(viewport={"width":1600,"height":1100})
 page.goto(path.resolve().as_uri())
 actual=page.locator("script").last.text_content()
 expected=re.findall(r"<script>(.*?)</script>",path.read_text(encoding="utf-8"),re.S)[-1]
 assert sha(actual.encode())==sha(expected.encode()),"loaded-browser-script-identity"
 return page

def original_oracle(page,route,native,index):
 # Deliberately separate Python placement: explicit logical origin at2x.
 row=route[index];expected=Image.new("RGBA",(440,280),(217,224,229,255));draw=ImageDraw.Draw(expected)
 for x in range(0,440,20):draw.line((x,0,x,279),fill=(196,207,214,255))
 for y in range(0,280,20):draw.line((0,y,439,y),fill=(196,207,214,255))
 im=Image.open(native/f"{row['frame']:03}.png").convert("RGBA")
 im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)
 expected.alpha_composite(im,((row["draw_x"]-280)*2,(row["draw_y"]-215)*2))
 actual=bytes(page.evaluate("Array.from(original.getContext('2d').getImageData(0,0,440,280).data)"))
 return actual==expected.tobytes()

def reset(page):
 if page.evaluate("reviewState.playing"):page.locator("#play").click()
 while page.evaluate("reviewState.index")!=0:page.locator("#prev").click()

def fits_visible_route(page,route,reference,report):
 originals={f["frame"]:f for f in reference["frames"]};cartoons={f["frame"]:f for f in report["frames"]}
 geometry=page.locator("#cartoon").evaluate("c=>({factor:c.getBoundingClientRect().width/c.width,width:c.parentElement.clientWidth})")
 for row in route:
  origin=(row["draw_x"]-280)*2;native=originals[row["frame"]]["visible_bounds_exclusive"];cart=cartoons[row["frame"]]["filtered_alpha8_bounds_hd_exclusive"]
  left=min(origin+native[0]*2,origin+cart[0])*geometry["factor"]
  right=max(origin+native[2]*2,origin+cart[2])*geometry["factor"]
  if left<0 or right>geometry["width"]:return False
 return True

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--exports",type=Path,required=True);p.add_argument("--original-native",type=Path,required=True);p.add_argument("--output",type=Path,required=True);args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 html=args.output/"review.html";r=build(HERE/"review.py",args.exports,args.original_native,html)
 assert r.returncode==0,r.stderr
 reference=json.loads((HERE/"reference/metadata.json").read_text());route=reference["selected_route"]["draws"]
 selected_report=json.loads((args.exports/"export-report.json").read_text())
 results=[];mutants=[]
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch();page=open_page(browser,html);errors=[];page.on("pageerror",lambda e:errors.append(str(e)));page.wait_for_function("window.reviewState&&reviewState.ready")
  assert page.locator("#speed").input_value()=="1" and page.locator("#zoom").input_value()=="fit"
  assert not page.locator("#follow").is_checked() and not page.locator("#bounds").is_checked()
  assert not page.locator("#technical").evaluate("e=>e.open")
  assert page.evaluate("Object.keys(images.original).length===6&&Object.keys(images.cartoon).length===6")
  reset(page);assert original_oracle(page,route,args.original_native,0)
  print("SMOKE PASS page loaded12images; defaults; exact original first-frame pixel oracle",flush=True)
  assert not errors and page.locator("h1").inner_text()=="Johnny's new walking direction"
  assert "original executable palette/compositing" in page.locator("#technical").text_content()
  print("SMOKE PASS readable scope and no page errors",flush=True)
  for index,row in enumerate(route):
   state=page.evaluate("reviewState");assert state["index"]==index and state["frame"]==row["frame"]
   assert original_oracle(page,route,args.original_native,index),f"review.py original-coordinate-oracle:{index}"
   page.locator("#next").click()
  results.append("all23-original-coordinate-full-pixel-oracles-and-frameIDs")
  for width in [1280,1600]:
   page.set_viewport_size({"width":width,"height":1000});page.wait_for_timeout(80)
   assert fits_visible_route(page,route,reference,selected_report),f"fit-full-route-visibility:{width}"
  results.append("Fit-all23-both-subjects-visible-at1280-and1600")
  assert page.evaluate("reviewState.index")==0
  page.locator("#prev").click();assert page.evaluate("reviewState.index")==22
  page.locator("#repeat").uncheck();page.locator("#play").click();page.wait_for_timeout(300)
  assert page.evaluate("reviewState.index===22&&!reviewState.playing")
  results.append("last-frame-stop-with-repeat-disabled")
  page.locator("#repeat").check();reset(page);page.locator("#play").click();page.wait_for_timeout(220);page.locator("#play").click()
  assert 1<=page.evaluate("reviewState.index")<=4
  results.append("normal-speed-discrete-advance")
  reset(page);page.locator("#speed").select_option("2");page.locator("#play").click();page.wait_for_timeout(220);page.locator("#play").click()
  assert 2<=page.evaluate("reviewState.index")<=7
  results.append("double-speed-discrete-advance")
  page.locator("#zoom").select_option("1");assert page.locator("#original").evaluate("e=>e.style.width")=="440px"
  page.locator("#zoom").select_option("3");assert page.locator("#cartoon").evaluate("e=>e.style.width")=="1320px"
  page.locator("#follow").check();page.locator("#technical summary").click();page.locator("#bounds").check();page.locator("#bounds").uncheck();assert not errors
  results.append("zoom-follow-bounds-and-clean-console")
  page.close()
  content=html.read_text(encoding="utf-8")
  for label,old,new in [("original-coordinate-oracle", "const x=2*(row.draw_x-left)","const x=3*(row.draw_x-left)"),
                        ("normal-speed-discrete-advance","if(index+1<data.route.length)index++;","if(index+1<data.route.length)index+=0;"),
                        ("fit-full-route-visibility","Math.min(3,c.parentElement.clientWidth/c.width)","2")]:
   assert content.count(old)==1,label+": mutant anchor"
   path=args.output/(label+"-mutant.html");path.write_text(content.replace(old,new),encoding="utf-8",newline="\n")
   mutant=open_page(browser,path);mutant.wait_for_function("window.reviewState&&reviewState.ready");reset(mutant)
   if label=="original-coordinate-oracle":failed=not original_oracle(mutant,route,args.original_native,0)
   elif label=="normal-speed-discrete-advance":
    mutant.locator("#play").click();mutant.wait_for_timeout(220);mutant.locator("#play").click();failed=mutant.evaluate("reviewState.index")==0
   else:
    mutant.set_viewport_size({"width":1280,"height":1000});mutant.wait_for_timeout(80);failed=not fits_visible_route(mutant,route,reference,selected_report)
   assert failed,label+": mutant survived"
   mutants.append({"label":"review.py: "+label,"result":"FIRED","failure_count":1,"html_sha256":sha(path.read_bytes()),"witness":"loaded browser script digest matched mutated file; tested actual rendered pixels or timer state"});mutant.close()
  browser.close()
 with tempfile.TemporaryDirectory(prefix="review-input-probe-",dir=args.output) as temp:
  root=Path(temp);copy=root/"authoring";copy.mkdir();(copy/"reference").mkdir();shutil.copyfile(HERE/"review.py",copy/"review.py");shutil.copyfile(HERE/"reference/metadata.json",copy/"reference/metadata.json")
  exports=root/"exports";shutil.copytree(args.exports,exports);report_raw=(exports/"export-report.json").read_bytes();report=json.loads(report_raw);original_source=(copy/"review.py").read_text(encoding="utf-8")
  cases=[("review-reference-identity",lambda d:d.update(reference_sha256="0"*64),'require(report["reference_sha256"]==sha(reference_raw),"review-reference-identity")','require(True,"review-reference-identity")'),
         ("review-six-frame-contract",lambda d:d["frames"].pop(),'require([item["frame"] for item in report["frames"]]==[11,19,20,21,22,23],"review-six-frame-contract")','require(True,"review-six-frame-contract")'),
         ("review-cartoon-pixels:011",lambda d:d["frames"][0].update(padded_png_sha256="0"*64),'require(sha(cartoon_raw)==item["padded_png_sha256"],f"review-cartoon-pixels:{frame:03}")','require(True,f"review-cartoon-pixels:{frame:03}")')]
  for index,(label,change,old,new) in enumerate(cases):
   bad=json.loads(json.dumps(report));change(bad);(exports/"export-report.json").write_text(json.dumps(bad),encoding="utf-8")
   path=root/f"bad-{index}.html";r=build(copy/"review.py",exports,args.original_native,path)
   assert r.returncode==1 and r.stderr.strip()=="FAIL "+label and not path.exists(),label+": expected refusal"
   results.append(label+"-refused-before-page")
   assert original_source.count(old)==1
   (copy/"review.py").write_text(original_source.replace(old,new),encoding="utf-8",newline="\n")
   r=build(copy/"review.py",exports,args.original_native,root/f"mutant-{index}.html");assert r.returncode==0,label+": mutant survived refusal"
   mutants.append({"label":"review.py: "+label,"result":"FIRED","failure_count":1,"source_sha256":sha((copy/"review.py").read_bytes()),"witness":"fresh python -B prints exact changed source SHA"})
   (copy/"review.py").write_text(original_source,encoding="utf-8",newline="\n")
  (exports/"export-report.json").write_bytes(report_raw)
  r=build(copy/"review.py",exports,args.original_native,root/"restored.html");assert r.returncode==0 and (root/"restored.html").read_bytes()==html.read_bytes()
  results.append("restored-builder-byte-reproduction")
 evidence={"review_source_sha256":sha((HERE/"review.py").read_bytes()),"test_sha256":sha(Path(__file__).read_bytes()),"html_sha256":sha(html.read_bytes()),"smoke_passed":2,"regressions":results,"mutations":mutants,"timing_limit":"Headless Chromium wall-clock intervals checked in bounded ranges; no original-executable or native engine timing claim."}
 (args.output/"verification.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n")
 print(f"PASS {len(results)} regressions (23 full original pixel oracles); {len(mutants)} executed-source mutations FIRED")

if __name__=="__main__":main()
