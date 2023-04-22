from flask import Flask, render_template, request,render_template_string,flash
from Writing import ielts
import os
from speaking import Speaking
from score_gen import save_score_plot
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

obj = ielts()
o = Speaking()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/writing', methods=["POST"])
def writing():
    return render_template("writing.html")

@app.route('/redirect')
def redirect():
    return render_template("writing.html")

@app.route('/writing/evaluate', methods=["POST"])
async def writing_evaluate():
    question = request.form["question"]
    answer = request.form["answer"]
    wordCount = request.form["hiddenWordCount"]
    wordCount = re.findall(r'\d+', wordCount)
    if answer=='':
        return render_template_string('<script>alert("Empty Question/Answer !!");window.location.href="/redirect"</script>')


    result = await obj.predictor(question_prompt=question,answer=answer,wordCount=wordCount)
   
    overall = result['predicted_score']
    task_achievement = result['task_achievement']
    cac = result['Coherence_and_cohesion']
    lexical = result['Lexical_resource']
    gram = result['Grammatical_range_and_accuracy']

    ovs = float(overall['score'])
    ovr = overall['remarks']
    tas = float(task_achievement['score'])
    tar = task_achievement['remarks']
    ccs = float(cac['score'])
    ccr = cac['remarks']
    les = float(lexical['score'])
    ler = lexical['remarks']
    grs = float(gram['score'])
    grr = gram['remarks']

    save_score_plot('overall', ovs)
    save_score_plot('task_achievement', tas)
    save_score_plot('coherence_cohesion', ccs)
    save_score_plot('lexical resources', les)
    save_score_plot('grammatical', grs)

    with open('results.txt','w') as f:
        f.write('Question Prompt :\n')
        f.write('{}\n\n'.format(question))
        f.write('Answer : \n{}\n\n'.format(answer))
        f.write('Writing Results :\n')
        f.write('Overall:\n\nScore: {}\nRemarks: {}\n'.format(ovs, ovr))
        f.write('Task Achievement:\n\nScore: {}\nRemarks: {}\n'.format(tas, tar))
        f.write('Coherence and Cohesion:\n\nScore: {}\nRemarks: {}\n'.format(ccs, ccr))
        f.write('Lexical Resources:\n\nScore: {}\nRemarks: {}\n'.format(les, ler))
        f.write('Grammatical Range and Accuracy:\n\nScore: {}\nRemarks: {}\n'.format(grs, grr))


    return render_template("result_writing.html", ovr=ovr, tar=tar, ccr=ccr, ler=ler, grr=grr)

@app.route('/speaking', methods=["POST"])
def speaking():
    return render_template('speaking.html')


@app.route('/speaking/upload',methods=["POST"])
def speaking_upload():
    uploaded_file = request.files['audio_file']
    filename = uploaded_file.filename
    ext = os.path.splitext(filename)[1]
    newfilename = 'speaking'+ext
    uploaded_file.save(os.path.join(app.root_path, 'static', newfilename))

    o.stt('static\speaking.mp3')
    transcript = open('transcript.txt','r').read()
    dialog = o.segment(transcript)
    result = o.speaking_predictor(dialog)

    gram = result['grammatical_range_and_accuracy']
    lexical = result['lexical_resources']
    coherence = result['coherence']
    overall = result['predicted_score']

    gs = float(gram['score'])
    ls = float(lexical['score'])
    cs = float(coherence['score'])
    ovs = float(overall['score'])

    gr = gram['remarks']
    lr = lexical['remarks']
    cr = coherence['remarks']
    ovr = overall['remarks']

    gc = gram['correction']
    lc = lexical['correction']
    cc = coherence['correction']
    

    save_score_plot('overalls',ovs)
    save_score_plot('coherences',cs)
    save_score_plot('lexicals',ls)
    save_score_plot('grams',gs) 

    with open('results.txt','w') as f:
        f.write('Speaking Results\n')
        f.write('Overall:\n\nScore: {}\nRemarks: {}\n'.format(ovs, ovr))
        f.write('Grammatical Range and Accuracy\n\nScore: {}\nRemarks: {}\nCorrection: {}\n'.format(gs, gr, gc))
        f.write('Lexical Resources\n\nScore: {}\nRemarks: {}\nCorrection: {}\n'.format(ls, lr, lc))
        f.write('Coherence\n\nScore: {}\nRemarks: {}\nCorrection: {}\n'.format(cs, cr, cc))


    return render_template("result_speaking.html",gr=gr, lr = lr, cr = cr, ovr = ovr, gc = gc, lc = lc, cc = cc)


@app.route('/result',methods=["POST"])
def result():
    return render_template("result.html")


@app.route('/result/send',methods=["POST"])
def send_result():
    sender = "donotreplyasimabot@gmail.com"
    receiver = request.form["email"]
    if receiver=='':
        return render_template_string('<script>alert("Empty Email.. Fill it !!");window.history.back()</script>')
    
    #create message container
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = "IELTS evaluation report"

    # add body to email
    body = "Please check your IELTS evaluation result"
    msg.attach(MIMEText(body, 'plain'))

    # add file attachment
    with open("results.txt", 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype="txt")
        attachment.add_header('Content-Disposition', 'attachment', filename="file.txt")
        msg.attach(attachment)

    # send the message via Gmail SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, "rmwdghaetbjtrfke") # replace "password" with your Gmail account password
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()

    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
