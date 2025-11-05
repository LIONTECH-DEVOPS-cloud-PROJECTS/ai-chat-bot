// Nyonga WhatsApp Admissions Bot webhook for Vercel (fixed config)
import sgMail from "@sendgrid/mail";

const {
  WABA_PHONE_ID,
  WABA_TOKEN,
  WABA_VERIFY_TOKEN,
  SENDGRID_API_KEY,
  LEADS_TO,
  NEXT_COHORT_DATE = "2026-01-28",
  BRAND = "LionTech Academy",
  CONTACT_PHONE = "+16473818836"
} = process.env;

if (SENDGRID_API_KEY) sgMail.setApiKey(SENDGRID_API_KEY);
const leadEmails = (LEADS_TO || "").split(",").map(s=>s.trim()).filter(Boolean);

// Send a WhatsApp message via Cloud API
async function sendWA(to, text, buttons=[]) {
  const url = `https://graph.facebook.com/v21.0/${WABA_PHONE_ID}/messages`;
  const body = buttons.length ? {
    messaging_product: "whatsapp",
    to,
    type: "interactive",
    interactive: {
      type: "button",
      body: { text },
      action: { buttons: buttons.map((b,i)=>({ type: "reply", reply: { id: `b${i}`, title: b } })) }
    }
  } : {
    messaging_product: "whatsapp",
    to,
    type: "text",
    text: { body: text }
  };
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${WABA_TOKEN}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!resp.ok) {
    console.error("WA send error", resp.status, await resp.text());
  }
}

// Email the lead to admissions
async function emailLead(lead) {
  if (!SENDGRID_API_KEY || !leadEmails.length) return;
  const msg = {
    to: leadEmails,
    from: { email: "no-reply@liontech.academy", name: "Nyonga Admissions Bot" },
    subject: `New WhatsApp lead: ${lead.full_name} — ${lead.program} (${lead.eligibility})`,
    html: `<h2>New ${BRAND} Lead</h2>
      <p><b>Name:</b> ${lead.full_name}</p>
      <p><b>Email:</b> ${lead.email}</p>
      <p><b>Phone:</b> ${lead.phone}</p>
      <p><b>Program:</b> ${lead.program}</p>
      <p><b>Eligibility:</b> ${lead.eligibility}</p>
      <p><b>Next Cohort:</b> ${NEXT_COHORT_DATE}</p>`
  };
  try { await sgMail.sendMultiple(msg); } catch (e) { console.error("SendGrid error", e?.response?.body || e); }
}

const PROGRAMS = [
  "DevOps Training Program",
  "Cyber Security and AI",
  "Cloud Computing",
  "AI and Pathways"
];

const AI_PATHWAYS = [
  "AI For Business Operations",
  "AI for Entrepreneurs and Innovations",
  "AI for Web Development and Branding",
  "AI for Social Media Marketing"
];

function eligibility(s) {
  const e = s.diploma==="yes" && (s.can_pay==="yes"||s.can_pay==="plan") && (s.laptop==="yes"||s.laptop==="plan");
  const c = s.diploma==="yes" && (s.can_pay==="plan"||s.laptop==="plan");
  return e ? "eligible" : c ? "conditional" : "not_eligible";
}

export default async function handler(req, res) {
  if (req.method === "GET") {
    const mode = req.query["hub.mode"];
    const token = req.query["hub.verify_token"];
    const challenge = req.query["hub.challenge"];
    if (mode === "subscribe" && token === WABA_VERIFY_TOKEN) return res.status(200).send(challenge);
    return res.sendStatus(403);
  }

  if (req.method !== "POST") return res.status(405).send("Method Not Allowed");

  const entry = req.body?.entry?.[0]?.changes?.[0]?.value;
  const msg = entry?.messages?.[0];
  if (!msg) return res.status(200).end();

  const from = msg.from;
  const text = msg.text?.body || msg.interactive?.button_reply?.title || msg.interactive?.list_reply?.title || "";

  // NOTE: Serverless functions are stateless; for production, add Redis. Here we keep a tiny in-memory map per process.
  global.__MEM ||= new Map();
  let s = global.__MEM.get(from) || { step: "greet" };

  if (s.step === "greet") {
    s.step = "program";
    await sendWA(from, `Welcome to ${BRAND}! Let’s get you into the right program.\nWhich program are you interested in?`, PROGRAMS);
  } else if (s.step === "program") {
    s.program = text;
    if (/AI and Pathways/i.test(text)) {
      s.step = "ai_pathway";
      await sendWA(from, "Which AI pathway?", AI_PATHWAYS);
    } else {
      s.step = "name";
      await sendWA(from, `Great choice—${s.program}. What’s your full name?`);
    }
  } else if (s.step === "ai_pathway") {
    s.program = text;
    s.step = "name";
    await sendWA(from, `Great choice—${s.program}. What’s your full name?`);
  } else if (s.step === "name") {
    s.name = text.trim();
    s.step = "can_pay";
    await sendWA(from, "Students pay CAD $1,000. Are you able to pay?", ["Yes", "Not now", "Need a plan"]);
  } else if (s.step === "can_pay") {
    s.can_pay = /yes/i.test(text) ? "yes" : /plan/i.test(text) ? "plan" : "no";
    s.step = "diploma";
    await sendWA(from, "Do you have a high school diploma or equivalent?", ["Yes","No"]);
  } else if (s.step === "diploma") {
    s.diploma = /yes/i.test(text) ? "yes" : "no";
    s.step = "laptop";
    await sendWA(from, "Do you have a laptop (or plan to get one within 2 weeks)?", ["Yes","No","Plan"]);
  } else if (s.step === "laptop") {
    s.laptop = /yes/i.test(text) ? "yes" : /plan/i.test(text) ? "plan" : "no";
    s.step = "email";
    await sendWA(from, "What’s the best email for your admission updates?");
  } else if (s.step === "email") {
    s.email = text.trim();
    s.step = "city";
    await sendWA(from, "Which city are you in?");
  } else if (s.step === "city") {
    s.city = text.trim();
    s.eligibility = eligibility(s);
    if (s.eligibility === "eligible") {
      s.step = "eligible_next";
      await sendWA(from, `✅ ${s.name}, you’re eligible for ${s.program}.\nNext cohort starts ${NEXT_COHORT_DATE}.\nWould you like to schedule an orientation call now or chat with a human?`, ["Schedule orientation","Chat with a human"]);
    } else if (s.eligibility === "conditional") {
      s.step = "conditional_next";
      await sendWA(from, `⚠️ ${s.name}, you’re conditionally eligible.\nConfirm a payment plan and/or secure a laptop to proceed.\nStart application or discuss a plan with an advisor?`, ["Start application","Discuss plan"]);
    } else {
      s.step = "not_eligible_next";
      await sendWA(from, `Thanks, ${s.name}. You’re not eligible yet.\nYou may re-apply after obtaining a diploma/GED and confirming payment/laptop.\nWould you like GED or laptop resources?`, ["GED resources","Laptop options"]);
    }

    emailLead({
      source: "whatsapp",
      phone: from,
      full_name: s.name,
      email: s.email,
      city: s.city,
      program: s.program,
      can_pay: s.can_pay,
      diploma: s.diploma,
      laptop: s.laptop,
      eligibility: s.eligibility
    }).catch(() => {});
  } else if (/Schedule orientation/i.test(text)) {
    s.step = "orientation_schedule";
    await sendWA(from, `Great! Share 2–3 times that work for you (with timezone), or say "ASAP" and we’ll reach out. A human can also call/text ${CONTACT_PHONE}.`);
  } else if (/Chat with a human/i.test(text)) {
    s.step = "human_handoff";
    await sendWA(from, `Connecting you to admissions now. You can also call/text ${CONTACT_PHONE}.`);
  } else {
    await sendWA(from, "Need anything else?\n• FAQs • Start application • Talk to a human");
  }

  global.__MEM.set(from, s);
  return res.status(200).end();
}
