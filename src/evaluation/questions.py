import json
from pathlib import Path

academic = "undergraduate-academic-policies"

original_questions = [
    ("001", "Can I take more than 36 credits in one semester", ["3.3.7"], [5], ["0018"]),
    ("002", "If I fail a course, can I retake it?", ["3.20.1"], [15, 16], ["0077"]),
    ("003", "Will withdrawing from a course affect my GPA?", ["3.3.12"], [5], ["0022"]),
    ("004", "What happens if I miss too many classes?", ["3.4.2", "3.4.3", "3.4.4", "3.4.5"], [6], ["0023", "0024", "0025"]),
    ("005", "How many semesters can I stay on academic probation?", ["3.16.4", "3.16.5"], [14], ["0067"]),
]

questions = []
for question_id, text, sections, pages, chunk_numbers in original_questions:
    questions.append({
        "question_id": question_id,
        "question": text,
        "language": "en",
        "source": "generated",
        "group": "answerable",
        "expected_sections": sections,
        "expected_pages": pages,
        "relevant_chunk_ids": [f"{academic}-{number}" for number in chunk_numbers],
    })

# Each row contains the question, language, group, supporting chunks, and notes.
student_questions = [
    (
        "if my adviser is on annual summer leave, then will he able to respond to my student request in registrar only when he comes back?",
        "en", "unanswerable", [],
        "The corpus does not describe adviser coverage or response times during annual leave.",
    ),
    (
        "What should I do if I didn’t receive EDMS contract signing yet?",
        "en", "unanswerable", [],
        "Ask what type of contract it is and when the signing request was expected.",
    ),
    (
        "кому обратиться если не получается подписать договор?",
        "ru", "unanswerable", [],
        "Ask what type of contract it is and what happens when the student tries to sign.",
    ),
    (
        "How can I contact school office to request for excusal from classes? did not get an answer from seds gmail",
        "en", "partial", [f"{academic}-0026"],
        "The instructor approves the absence. A SEDS contact or follow-up channel was not found.",
    ),
    (
        "Who can I ask about withdrawal of an internship?",
        "en", "unanswerable", [],
        "Ask what type of internship it is and whether it is already registered.",
    ),
    (
        "What should I do if I unsubscribe from the seds, all students and campus 22 in gmail",
        "en", "unanswerable", [],
        "No instructions for restoring these subscriptions were found.",
    ),
    (
        "Where can I get the certificate that i study in the uni? I need it for the visa.",
        "en", "unanswerable", [],
        "Students can request Enrollment Verification through the Registrar website during working hours. The mobility guidebook mentions the form but does not include the request procedure.",
    ),
    (
        "is there a site or page to know what could be counted as an excused absence and what documents are needed?",
        "en", "partial", [f"{academic}-0023", f"{academic}-0025", f"{academic}-0026"],
        "The policies describe attendance and approval. A single page listing qualifying reasons and required documents was not found.",
    ),
    (
        "where can I get the certificate of illness?",
        "en", "unanswerable", [],
        "This question concerns a certificate for a class absence. The Health and Well-being Department email explains where to obtain it, but the email is outside the current corpus.",
    ),
    (
        "Где можно цены на дорм посмотреть?",
        "ru", "answerable", ["dormitory-accommodation-rules-0022"],
        "Section 3.1.10, page 5, identifies MyNU as the place to check approved rates. Local corpus only.",
    ),
    (
        "У нас в университете есть Erasmus программы, или какие то государственные программы по обмену, где все оплачивается полностью?",
        "ru", "partial", ["academic-mobility-guidebook-2026-0017", "student-mobility-policy-0037"],
        "The sources mention Erasmus+ and government-funded programs. Full coverage depends on the specific opportunity.",
    ),
    (
        "Придет ли стипендия если карта просрочилась?",
        "ru", "unanswerable", [],
        "The corpus does not explain how an expired card affects payment. The bank account and payment details matter.",
    ),
    (
        "к кому можно обратиться по поводу неисправных тренажеров в джиме?",
        "ru", "answerable", ["sports-complex-rules-0093"],
        "Clause 96 says to report equipment malfunctions to the Sports Complex administration.",
    ),
    (
        "is it possible to get an excused absence if youre going to a conference? if so, how do you do it?",
        "en", "partial", [f"{academic}-0026"],
        "The instructor approves absences. A conference-specific rule and document list were not found.",
    ),
    (
        "Where can we complain about dormitory service?",
        "en", "unanswerable", [],
        "A general complaint channel was not found. Ask what the service issue concerns.",
    ),
    (
        "If I want to change schools should I request it in registrar now?",
        "en", "partial", [f"{academic}-0035", f"{academic}-0036"],
        "The sources describe eligibility and the Transfer between Schools form in SIS. They do not establish whether applications are open now.",
    ),
    (
        "Will I be able to leave my belongings in the dormitory after I receive confirmation of my withdrawal? (Summer course)",
        "en", "unanswerable", [],
        "Rules about leaving NU or eviction do not establish what happens after withdrawing from a single summer course.",
    ),
    (
        "are there any financial obligations if a student drops out of the university after 2nd year?",
        "en", "unanswerable", [],
        "Ask which obligations the student means and what funding or contract terms apply.",
    ),
    (
        "are there any limitation on the number of credits you can take on summer?",
        "en", "unanswerable", [],
        "An explicit Summer term maximum was not found. The ordinary semester limit alone does not establish it.",
    ),
    (
        "кому писать репорт если мою айдишку забрали и воспользовались?",
        "ru", "partial", ["campus-access-security-rules-0013"],
        "The lost-card reporting procedure applies. A specific channel for reporting misuse was not found.",
    ),
    (
        "если экстра плейс одобрили, но в расписании уже 36 кредитов, нужно дропнуть курс чтобы место для него было? типа автоматом зарегается или как? подскажите пожалуйста",
        "ru", "partial", ["undergraduate-academic-policies-0018", "undergraduate-academic-policies-0019"],
        "The sources explain the credit limit and overload process. They do not explain extra-place auto-registration.",
    ),
    (
        "Что можно сделать если проф в регистраре неправильную оценку поставил? Это же окончательно? Если окончательно куда можно заяву накатать на него? Подскажите пожалуйста",
        "ru", "answerable", ["undergraduate-academic-policies-0072", "undergraduate-academic-policies-0073", "undergraduate-academic-policies-0074", "undergraduate-academic-policies-0075", "undergraduate-academic-policies-0076"],
        "Incorrect grade entry is grounds for appeal. The procedure depends on whether it is an exam grade or a final course grade.",
    ),
    (
        "Как можно запустить на кампус родственников? И что им нужно с собой иметь? Подскажите пожалуйста",
        "ru", "partial", ["campus-access-security-rules-0014", "campus-access-security-rules-0015"],
        "Security may ask for identification and access documents. The booking procedure for student relatives was not confirmed.",
    ),
    (
        "Подскажите пожалуйста гостей на кампус пускают без запроса секюрити?",
        "ru", "partial", ["campus-access-security-rules-0040"],
        "The security request applies to the visitor category described in the source. A general rule for student guests was not confirmed.",
    ),
    (
        "Можете подсказать, имеет ли проф право ставить F за курс из за низкого attendance-a?",
        "ru", "partial", ["undergraduate-academic-policies-0025"],
        "Attendance may affect the grade. The source does not explicitly authorize an F for low attendance.",
    ),
    (
        "подскажите где можно найти документ где написаны правила как составляются силлабусы, какие полиси профы могут делать и тд?",
        "ru", "partial", ["undergraduate-academic-policies-0025"],
        "The source states an attendance disclosure requirement. A general syllabus policy was not found.",
    ),
    (
        "подскажите, пожалуйста, а магистранты тоже получают дорожку (state grant)?",
        "ru", "unanswerable", [],
        "Clarify whether this means travel reimbursement, an educational grant, or another payment.",
    ),
    (
        "Подскажите, пожалуйста, как заполнять форму overload, если курс будет регистрироваться через extra place и его пока нет в расписании?",
        "ru", "partial", ["undergraduate-academic-policies-0018", "undergraduate-academic-policies-0019"],
        "The sources explain where to submit the form and who approves it. Instructions for an extra-place course were not found.",
    ),
    (
        "Подскажите, пожалуйста, у кого можно получить справку об absence of academic and non-academic misconducts?",
        "ru", "unanswerable", [],
        "The corpus does not identify who issues this certificate.",
    ),
    (
        "не подскажете как нужно делать retake по курсам? Как и когда заполнять форму?",
        "ru", "partial", ["undergraduate-academic-policies-0077", "undergraduate-academic-policies-0078"],
        "The policy describes retake eligibility and grading. The form and submission deadlines were not found.",
    ),
]
student_questions.extend([
    (
        "Is retaking courses (UG) paid?, if so where can I check the price?",
        "en", "partial",
        [f"{academic}-0078", f"{academic}-0079"],
        "A retake may be charged. Section 3.20.3 identifies who approves the cost and payment process, but does not say where students can check the price.",
    ),
    (
        "Мой retake form аппрувнули но регистрар не дал мне зарегать калк 1 Что делать?",
        "ru", "partial",
        [f"{academic}-0019", f"{academic}-0020"],
        "The policy describes possible registration holds and identifies SIS as the official registration record. It does not resolve the individual case after retake approval.",
    ),
    (
        "Может ли проф ставить 0 за экзамен и homework, пропущенные за время болезни (справка есть)?",
        "ru", "partial",
        [f"{academic}-0025", f"{academic}-0026"],
        "The policy covers attendance rules, instructor approval and disputes. Whether a zero can be assigned for the missed assessments depends on the course syllabus, which is outside the current corpus.",
    ),
    (
        "how many 1 credit costs in NU?",
        "en", "unanswerable", [],
        "No price per ECTS was found in the current corpus.",
    ),
    (
        "Can I register 30+ credits if I am on probation?",
        "en", "answerable",
        [f"{academic}-0017"],
        "Section 3.3.6 sets a maximum of 30 ECTS during academic probation. In some cases the limit may be reduced to 24 ECTS.",
    ),
    (
        "Accoeding to the handbook, iam left to register for only 3 courses. Am i allowed to go underload on credits in that case?",
        "en", "partial",
        [f"{academic}-0016", f"{academic}-0017"],
        "Section 3.3.5 allows students to request an underload through SIS in exceptional circumstances. Approval of this case depends on the required decision-makers.",
    ),
    (
        "24 credits is ok for fall semester 1 years?",
        "en", "partial",
        [f"{academic}-0016", f"{academic}-0019"],
        "24 eligible ECTS meets the general full-time minimum. First-year, first-semester students may also have required courses assigned through block registration.",
    ),
    (
        "How to contact a bursar's office if they don't reply to an email?",
        "en", "unanswerable", [],
        "No alternative contact or escalation channel for an unanswered email was found in the corpus.",
    ),
    (
        "if i am studying 2nd year, I will be enrolled for 3rd year by the july 2027?",
        "en", "partial",
        [f"{academic}-0080"],
        "Section 3.21.2 gives the second-year progress requirement of at least 90 ECTS. It does not establish the student's enrollment status by July 2027.",
    ),
    (
        "do our comp labs have origin/origin pro installed?",
        "en", "unanswerable", [],
        "No computer lab software inventory or reference to OriginPro was found in the corpus.",
    ),
    (
        "What does probation mean here? Sorry, I'm a freshman",
        "en", "answerable",
        [f"{academic}-0063", f"{academic}-0064", f"{academic}-0065"],
        "Sections 3.16.2 and 3.16.4 define good academic standing and explain when students are placed on academic probation.",
    ),
    (
        "if a student receives two probations in a row, is he/she obligatory expelled from the university?",
        "en", "answerable",
        [f"{academic}-0066", f"{academic}-0067"],
        "Sections 3.16.4 and 3.16.5 cover dismissal after extended probation and the exceptional approval of an additional semester of study. Labeled against the current corpus edition.",
    ),
    (
        "How long does it take for voluntary withdrawal to process?",
        "en", "partial",
        ["leave-dismissal-withdrawal-0085", "leave-dismissal-withdrawal-0086"],
        "Annex 5 explains the process and when the decision takes effect. It does not specify a processing time.",
    ),
    (
        "What is the deadline for Course Withdrawal request?",
        "en", "partial",
        [f"{academic}-0021"],
        "Section 3.3.12 points to the withdrawal deadline in the Academic Calendar. The exact date depends on the term.",
    ),
    (
        "Are there any guides to find book location in the library (?)",
        "en", "partial",
        ["library-rules-0013", "library-rules-0027"],
        "The library policy provides for instructions and electronic catalog training. The reviewed sections do not contain a guide for locating a book on the shelf.",
    ),
])
student_questions.extend([
    (
        "What is the GPA for Dean's list and higher stipend?",
        "en", "answerable",
        [f"{academic}-0057", "stipend-support-policy-0020"],
        "Dean's List requires a GPA of 3.75. Bachelor's students with a semester GPA of at least 3.67 receive a 15% stipend increase. Both chunks are needed for the full answer.",
    ),
    (
        "Retake is possible only in case of fail?",
        "en", "answerable",
        [f"{academic}-0077"],
        "Section 3.20.1 allows a retake when the grade prevents academic progress. Retakes solely to increase GPA or CGPA are prohibited.",
    ),
    (
        "Probation начинается если gpa ниже 2.0?",
        "ru", "answerable",
        [f"{academic}-0063", f"{academic}-0064"],
        "At the end of fall and spring semesters, both GPA and CGPA must be at least 2.00 for Good Academic Standing. Failing either condition leads to academic probation.",
    ),
    (
        "Как считать gpa за семестр если мы взяли какой-то курс для пересдачи?",
        "ru", "answerable",
        [f"{academic}-0078"],
        "Section 3.20.2 counts each attempt in its respective semester GPA. Only the last retake counts toward the final CGPA.",
    ),
    (
        "можно академ брать со второго семестра первого курса?",
        "ru", "answerable",
        [
            "leave-dismissal-withdrawal-0015",
            "leave-dismissal-withdrawal-0016",
            "leave-dismissal-withdrawal-0026",
        ],
        "First-year undergraduates are ineligible under the Other category. Medical and Immediate Family Member leave remain possible subject to the general eligibility rules and application windows.",
    ),
    (
        "А как академ брать",
        "ru", "answerable",
        [
            "leave-dismissal-withdrawal-0014",
            "leave-dismissal-withdrawal-0015",
            "leave-dismissal-withdrawal-0018",
            "leave-dismissal-withdrawal-0055",
            "leave-dismissal-withdrawal-0056",
        ],
        "Select the leave category, submit the application and required documents through SIS within the applicable window, and wait for the decision to be registered.",
    ),
    (
        "где можно найти underload form?",
        "ru", "answerable",
        [f"{academic}-0016", f"{academic}-0017"],
        "Section 3.3.5 says the Course Underload Form is available in SIS.",
    ),
    (
        "Deadline major declaration когда?",
        "ru", "answerable",
        [f"{academic}-0027", f"{academic}-0028"],
        "Section 3.5.1 requires declaration of the primary major by the end of the first year and acceptance into it by the end of the second year.",
    ),
    (
        "какой дедлайн для minor declaration?",
        "ru", "answerable",
        [f"{academic}-0030"],
        "Section 3.6.1 sets the deadline at the end of the first semester of the student's final year, subject to School approval.",
    ),
    (
        "No incomplete grades in any courses это fail/withdrawal?",
        "ru", "answerable",
        [f"{academic}-0050", f"{academic}-0054", f"{academic}-0056"],
        "Incomplete is a temporary I grade. F and W are separate grades. An unresolved I may revert to F under the conditions in section 3.11.4.",
    ),
    (
        "Incomplete grade лишает стипендии несмотря на серьезную причину?",
        "ru", "answerable",
        [
            "stipend-support-policy-0013",
            "stipend-support-policy-0014",
            "stipend-support-policy-0015",
        ],
        "Under clause 19, eligible bachelor's and master's students with a valid documented reason can receive the stipend after completing the course requirements, with payment covering the eligible period from the start of the semester.",
    ),
    (
        "если на летнике взять incomplete grade степа будет капать?",
        "ru", "answerable",
        [
            "stipend-support-policy-0014",
            "stipend-support-policy-0015",
            "stipend-support-policy-0017",
            "stipend-support-policy-0018",
        ],
        "Summer break payments are based on spring results. For bachelor's students who take summer courses, the fall award is also based on spring results. For master's students whose summer semester is part of the curriculum, the fall award is based on summer results. Clause 19 covers documented Incomplete grades.",
    ),
    (
        "Как работает honors designation для магистрантов?",
        "ru", "answerable",
        ["graduation-policy-0009", "graduation-policy-0010"],
        "Clause 8 awards Distinction at a CGPA of 4.00. After excluding those graduates, the top 10% in each master's program qualify for Graduated with Honors, with fractional counts rounded up.",
    ),
    (
        "Какой cGPA должен быть для красного диплома?",
        "ru", "answerable",
        [
            "graduation-policy-0007",
            "graduation-policy-0008",
            "graduation-policy-0009",
            "graduation-policy-0010",
        ],
        "Undergraduate thresholds are 3.67 for Cum Laude, 3.80 for Magna Cum Laude, 3.90 for Summa Cum Laude, and 4.00 for Distinction. Master's honors follow the separate rules in clause 8.",
    ),
    (
        "у нас есть что-то вроде course overload form? чтобы больше 36 кредитов за семестр зарегать, чето в регистраторе не вижу",
        "ru", "answerable",
        [f"{academic}-0018", f"{academic}-0019"],
        "Section 3.3.7 places the Course Overload Form in SIS. Requests above 36 ECTS require School approval and final approval from the VPAA.",
    ),
])
contract_questions = {"real-002", "real-003"}

for number, (text, language, group, relevant_ids, notes) in enumerate(student_questions, start=1):
    question_id = f"real-{number:03d}"
    question = {
        "question_id": question_id,
        "question": text,
        "language": language,
        "source": "real_student",
        "group": group,
        "relevant_chunk_ids": relevant_ids,
        "notes": notes,
    }

    if question_id in contract_questions:
        question["topic"] = "contract_signing"

    questions.append(question)

output_path = Path("data/eval/questions.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as json_file:
    json.dump(questions, json_file, ensure_ascii=False, indent=2)

print(f"Saved {len(questions)} questions to {output_path}")