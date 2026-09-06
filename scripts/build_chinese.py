"""Generate the Chinese page from the English page and reviewed translations."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import json

root=Path(__file__).resolve().parents[1]
s=BeautifulSoup((root/'index.html').read_text(encoding='utf-8'),'html.parser')
s.html['lang']='zh-CN'
s.title.string='杨奕铭 | 自动驾驶与视觉智能'
s.select_one('link[rel=canonical]')['href']='https://yimingyang23.github.io/zh.html'
for el in s.select('meta[property="og:url"]'):el['content']='https://yimingyang23.github.io/zh.html'
s.select_one('meta[name=description]')['content']='Yiming Yang，香港中文大学（深圳）博士生，研究车道拓扑推理、世界模型与视觉语言模型。查看论文、研究演示、学术经历与中英文简历。'
s.select_one('meta[property="og:title"]')['content']='Yiming Yang · 自动驾驶与视觉智能'
s.select_one('meta[property="og:description"]')['content']='研究论文、动态演示与学术经历。香港中文大学（深圳）· 即将访问南洋理工大学 AutoMan Lab。'
translations={
'Skip to content':'跳转到正文','About':'关于我','Demos':'研究演示','Publications':'研究论文','Experience':'教育经历','Service':'学术服务',
'Shenzhen, China':'中国 · 深圳','AUTONOMOUS DRIVING · VISUAL INTELLIGENCE':'自动驾驶 · 视觉智能','Ph.D. student at':'博士研究生 ·','CUHK-Shenzhen':'香港中文大学（深圳）',
'Next: NTU AutoMan Lab':'下一站：南洋理工大学 AutoMan Lab','Incoming visiting Ph.D. student · Oct 2026–Oct 2027 · Host:':'访问博士生（即将开始）· 2026.10–2027.10 · 合作导师：','Prof. Chen Lv (吕辰)':'吕辰教授','CSC Scholar · 2026':'CSC 奖学金 · 2026',
'Latest updates':'近期动态','RESEARCH & COMMUNITY':'研究进展 · 学术交流','2026 / 2027':'2026 / 2027','AUG 2026':'2026 年 8 月','MAY 2026':'2026 年 5 月',
'Serving as a reviewer for':'担任以下会议审稿人：','ICLR 2027, NeurIPS 2026, and AAAI 2027.':'ICLR 2027、NeurIPS 2026、AAAI 2027。','Publication':'论文发表','Award':'奖学金',
'RESEARCH IN ACTION':'动态研究展示','Scene understanding, in motion.':'在连续场景中理解道路。','2 PROJECTS / 8 SCENES':'2 个项目 / 8 组场景','Explore how temporal models and vision-language models represent road geometry and lane relationships.':'从时序建模到视觉语言推理，探索道路几何与车道连接关系的表达方式。',
'Temporal lane topology':'时序车道拓扑','Vision-language reasoning':'视觉语言推理','Scene 01 · 1 / 6':'场景 01 · 1 / 6','Scene 05 · 1 / 2':'场景 05 · 1 / 2','Choose a scene below':'点击下方缩略图切换场景','Open video':'打开视频',
'PAPERS & PREPRINTS':'论文与预印本','All on Google Scholar ↗':'在 Google Scholar 查看 ↗','All research':'全部研究','Autonomous driving':'自动驾驶','Cross-modal recognition':'跨模态识别','Other vision':'其他视觉研究','PUBLICATIONS / PREPRINTS':'论文 / 预印本','Search publications':'搜索论文','Paper':'论文','Code':'代码','Code & data':'代码与数据','Copy citation':'复制引用','Download .bib':'下载 .bib','No publications match your search. Try another keyword or topic.':'没有匹配的论文，请尝试其他关键词或研究方向。',
'EDUCATION & RESEARCH VISIT':'教育与学术访问','Academic journey':'学术经历','Full curriculum vitae ↓':'下载完整简历 ↓','OCT 2026 — OCT 2027':'2026.10 — 2027.10','AUG 2024 — PRESENT':'2024.08 — 至今','AUG 2021 — JUN 2024':'2021.08 — 2024.06','AUG 2017 — JUN 2021':'2017.08 — 2021.06','Incoming':'即将开始','Nanyang Technological University':'南洋理工大学','The Chinese University of Hong Kong, Shenzhen':'香港中文大学（深圳）','Sun Yat-sen University':'中山大学','Northwest A&F University':'西北农林科技大学',
'Visiting Ph.D. Student · AutoMan Lab · Singapore':'访问博士生 · AutoMan Lab · 新加坡','Host: Prof. Chen Lv · China Scholarship Council (CSC)':'合作导师：吕辰教授 · 国家留学基金管理委员会（CSC）资助','Ph.D. in Computer and Information Engineering':'计算机与信息工程博士研究生','Advisors: Prof. Zhen Li & Prof. Shuguang Cui · Full scholarship':'导师：李镇教授、崔曙光教授 · 全额奖学金','M.S. in Electronics and Communication Engineering':'电子与通信工程硕士','Advisor: Prof. Haifeng Hu · Ranked 1st in comprehensive evaluation':'导师：胡海峰教授 · 综合测评第 1 名','B.E. in Electronics and Information Engineering':'电子信息工程学士','GPA: 3.85 / 4.00 · Top 2.94%':'GPA：3.85 / 4.00 · 前 2.94%',
'Honors & awards':'荣誉与奖励','CSC Scholarship':'国家公派留学奖学金（CSC）','Overseas research visit · Awarded May 2026':'支持海外学术访问 · 2026 年 5 月获批','National Scholarship':'国家奖学金','Outstanding Master\'s Graduate':'优秀硕士毕业生','Excellent Master\'s Thesis · Sun Yat-sen University':'优秀硕士学位论文 · 中山大学','Excellent Bachelor\'s Thesis':'优秀本科毕业论文','SPECIAL GRADE':'特等','Guo Xie Bi Rong Scholarship':'郭谢碧蓉奖学金','Academic service':'学术服务','Conference reviewer':'会议审稿人','Workshop organizer':'研讨会组织者','Journal reviewer':'期刊审稿人','Teaching experience':'教学经历','Teaching Assistant · CUHK-Shenzhen':'助教 · 香港中文大学（深圳）',
'CIE6020: Information Theory · Fall 2025':'CIE6020：信息论 · 2025 年秋季','CIE6032: Selected Topics in Deep Learning Foundations and Their Applications · Summer 2026':'CIE6032：深度学习基础与应用专题 · 2026 年夏季','Robust and Generalized Lane Topology Understanding and HD Map Generation through CoT Design.':'通过思维链设计实现稳健、可泛化的车道拓扑理解与高精地图生成。',
'CONTACT':'联系我','Let\'s talk research.':'欢迎交流与合作。','I welcome conversations and collaborations in autonomous driving,':'欢迎围绕自动驾驶、车道拓扑推理与跨模态学习','lane topology reasoning, and cross-modal learning.':'开展学术交流和研究合作。','© 2026 Yiming Yang · Updated September 2026':'© 2026 Yiming Yang · 更新于 2026 年 9 月','Curriculum vitae':'个人简历','Back to top ↑':'返回顶部 ↑',
'Download CV':'下载简历','English CV':'英文简历','Chinese CV':'中文简历','Google Scholar':'谷歌学术','Email':'邮箱','Prof. Zhen Li':'李镇教授','Prof. Shuguang Cui':'崔曙光教授','Prof. Haifeng Hu':'胡海峰教授','Dr. Weipeng Hu':'胡伟鹏博士','All demo files':'全部演示文件',
}
translations.update({
'8 SELECTED SCENES':'8 组精选场景',
'Explore two perspectives on driving scenes: temporal modeling and vision-language understanding.':'从时序建模与视觉语言理解两个角度，观察驾驶场景。',
'Temporal modeling':'时序建模','Lane tracks across time':'跨帧车道轨迹','01 / TEMPORAL MODELING':'01 / 时序建模',
'Follow how lane geometry and connectivity evolve across consecutive driving frames.':'观察连续驾驶帧中车道几何与连接关系的变化，以及跨帧车道轨迹。',
'Select a scene to play. Use the controls to pause or view in full screen.':'选择场景即可播放，支持暂停与全屏查看。',
'VLM understanding':'VLM 理解','Visual-language scene understanding':'视觉语言场景理解','02 / VISION + LANGUAGE':'02 / 视觉与语言',
'Explore visual-language understanding through lane visualizations and structured text output.':'对照车道可视化与结构化文本输出，展示视觉语言模型对场景及车道关系的理解。',
'Select a scene to play. Open the video in full screen to read the text.':'选择场景即可播放，全屏查看可阅读完整文本。',
'Watch VLM scenes':'观看 VLM 场景','Your browser does not support video.':'你的浏览器不支持视频播放。','Open the video':'打开视频',
})
for i in range(1,7):translations[f'Scene {i:02d}']=f'场景 {i:02d}'
for node in list(s.find_all(string=True)):
 if node.parent.name in ['script','style','pre','title']:continue
 normalized=str(node).strip()
 if normalized in translations:node.replace_with(str(node).replace(normalized,translations[normalized]))
s.select_one('h1').clear();s.select_one('h1').append(BeautifulSoup('杨奕铭<span class="name-period">.</span><span class="roman-name">Yiming Yang</span>','html.parser'))
brand=s.select_one('.wordmark');brand.clear();brand.append(BeautifulSoup('<span class="monogram">YY</span> 杨奕铭','html.parser'))
paras=s.select('.profile-copy > p')
paras[1].clear();paras[1].append(BeautifulSoup('我研究自动驾驶系统如何<strong>感知道路场景、推理车道连接关系，并建模环境的时序变化</strong>。研究方向包括车道拓扑推理、世界模型与视觉语言模型。','html.parser'))
paras[2].clear();paras[2].append(BeautifulSoup('我的导师是<a href="https://sse.cuhk.edu.cn/faculty/lizhen">李镇教授</a>和<a href="https://sse.cuhk.edu.cn/en/faculty/cuishuguang">崔曙光教授</a>，同时与腾讯 T Lab 开展自动驾驶相关研究合作。此前，我在中山大学跟随<a href="https://seit.sysu.edu.cn/teacher/HuHaifeng">胡海峰教授</a>和<a href="https://ise.sysu.edu.cn/teacher/1492">胡伟鹏博士</a>研究跨模态人脸识别与行人重识别。','html.parser'))
news=s.select('.news-row p')
news[1].clear();news[1].append(BeautifulSoup('<a href="files/CoPo-KDD2026.pdf"><strong>CoPo</strong></a> 发表于 <strong>KDD 2026</strong>：以几何引导的表征实现一致的车道与交通拓扑推理。','html.parser'))
news[2].clear();news[2].append(BeautifulSoup('获得<strong>国家留学基金管理委员会（CSC）奖学金</strong>，支持赴南洋理工大学开展学术访问。','html.parser'))
for el in s.select('[placeholder]'):el['placeholder']='题目、作者或会议期刊' if el.get('id')=='paper-search' else el['placeholder']
for el in s.select('[aria-label]'):
 text=el['aria-label'];el['aria-label']=translations.get(text,text)
 if ' scene ' in text:el['aria-label']=text.replace(' scene ',' 场景 ')
for el in s.select('a[href="files/Yiming_Yang_CV.pdf"]'):
 if el.get('data-cv-language')!='en':el['href']='files/Yiming_Yang_CV_ZH.pdf'
for link in s.select('.language-switch a'):
 link.attrs.pop('aria-current',None)
 if link.get('lang')=='zh-CN':link['aria-current']='page'
for link in s.select('.profile-links a[data-cv-language]'):
 if 'primary' in link.get('class',[]):
  link['href']='files/Yiming_Yang_CV_ZH.pdf';label=' 中文简历'
 else:
  link['href']='files/Yiming_Yang_CV.pdf';label=' 英文简历'
 for text in list(link.find_all(string=True)):
  if str(text).strip():text.replace_with(label)
s.select_one('#result-count').string=f"{len(s.select('.paper'))} 篇论文与预印本"
for button in s.select('[data-scene]'):
 button['aria-label']=('时序建模 ' if button.find_parent(class_='demo-panel')['data-project']=='surround-view' else 'VLM 理解 ')+button.span.get_text(strip=True)
for venue in s.select('.venue'):
 if venue.get_text().startswith('Preprint'):venue.string=venue.get_text().replace('Preprint','预印本')
(root/'zh.html').write_text(str(s),encoding='utf-8')
print('Built Chinese page.')
