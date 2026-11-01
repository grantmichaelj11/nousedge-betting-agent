import os
import re

import mailtrap as mt
import markdown

# Nous Edge theme (matches the site's dark UI)
BG = "#0b0f17"          # page background
PANEL = "#111a2b"       # card / panel background
BORDER = "#24324d"      # card borders and dividers
TEXT = "#e6edf3"        # primary text
MUTED = "#9aa7b8"       # secondary text
BLUE = "#4a8fe0"        # "EDGE" blue, links
LABEL_BLUE = "#7fb3ff"  # column labels, subtitle
FONT = "-apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

# Email clients strip most <style> rules, so every element gets inline styles.
INLINE_STYLES = {
    "h1": (
        f"margin:0 0 24px;padding:24px;background-color:{PANEL};border:1px solid {BORDER};"
        f"border-radius:10px;color:{TEXT};font-size:24px;font-weight:600;text-align:center;"
    ),
    "h2": (
        f"margin:28px 0 12px;padding-bottom:10px;border-bottom:1px solid {BORDER};"
        f"color:{TEXT};font-size:18px;font-weight:600;"
    ),
    "p": f"margin:0 0 14px;color:{TEXT};font-size:14px;line-height:1.6;",
    "em": f"color:{MUTED};",
    "ul": f"margin:0 0 14px;padding-left:20px;color:{TEXT};",
    "li": f"margin:0 0 6px;color:{TEXT};font-size:14px;line-height:1.5;",
    "strong": f"color:{TEXT};font-weight:600;",
    "table": (
        f"width:100%;border-collapse:separate;border-spacing:0;background-color:{PANEL};"
        f"border:1px solid {BORDER};border-radius:10px;margin:0 0 16px;"
    ),
    "th": (
        f"padding:12px 14px 8px;text-align:left;color:{LABEL_BLUE};font-size:11px;"
        f"font-weight:600;letter-spacing:0.5px;text-transform:uppercase;"
        f"border-bottom:1px solid {BORDER};"
    ),
    "td": (
        f"padding:10px 14px;color:{TEXT};font-size:14px;"
        f"border-bottom:1px solid {BORDER};"
    ),
}
LINK_STYLE = f"color:{BLUE};text-decoration:none;word-break:break-all;"
# Section headings already have a divider line, so --- just adds spacing.
HR_STYLE = "border:none;margin:16px 0;"

# Bare URLs that aren't already part of a Markdown link or <autolink>.
BARE_URL = re.compile(r"(?<![(<])(https?://[^\s<>)]+)")


def _apply_theme(body_html: str) -> str:
    """Add the theme's inline styles to the HTML that the markdown package produces."""
    for tag, style in INLINE_STYLES.items():
        attrs = f' bgcolor="{PANEL}"' if tag == "table" else ""
        body_html = body_html.replace(f"<{tag}>", f'<{tag}{attrs} style="{style}">')
    body_html = body_html.replace("<a href=", f'<a style="{LINK_STYLE}" href=')
    body_html = body_html.replace("<hr />", f'<hr style="{HR_STYLE}" />')
    return body_html


def render_html(report_md: str) -> str:
    """Turn the agent's Markdown report into a themed HTML email."""
    report_md = BARE_URL.sub(r"<\1>", report_md)  # make plain URLs clickable
    body = _apply_theme(markdown.markdown(report_md, extensions=["tables", "nl2br"]))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="supported-color-schemes" content="dark">
</head>
<body bgcolor="{BG}" style="margin:0;padding:0;background-color:{BG};">
<div style="background-color:{BG};">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="{BG}" style="background-color:{BG};">
  <tr>
    <td align="center" bgcolor="{BG}" style="padding:0 16px;background-color:{BG};">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" bgcolor="{BG}" style="max-width:720px;font-family:{FONT};background-color:{BG};">
        <!-- Header -->
        <tr>
          <td bgcolor="{BG}" style="background-color:{BG};padding:22px 0;border-bottom:1px solid {BORDER};">
            <span style="font-size:26px;font-weight:700;letter-spacing:0.5px;color:{TEXT};">NOUS</span><span style="font-size:26px;font-weight:700;letter-spacing:0.5px;color:{BLUE};">EDGE</span>
          </td>
        </tr>
        <!-- Report -->
        <tr>
          <td bgcolor="{BG}" style="background-color:{BG};padding:28px 0 8px;color:{TEXT};">
            {body}
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td bgcolor="{BG}" style="background-color:{BG};padding:20px 0 32px;border-top:1px solid {BORDER};color:{MUTED};font-size:12px;">
            Nous Edge &middot; <span style="color:{LABEL_BLUE};">Bet Intelligently.</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</div>
</body>
</html>"""


def send_report(report_md: str, subject: str = "Nous Edge News Update", category: str = "News Report"):
    """Email a Markdown report through Mailtrap, as themed HTML with a plain-text fallback."""
    api_token = os.getenv("MAILTRAP")
    dev_email = os.getenv("DEV_EMAIL")

    mail = mt.Mail(
        sender=mt.Address(email="dev@nousedge.io", name="Nous Edge Team"),
        to=[mt.Address(email=dev_email)],
        subject=subject,
        text=report_md,              # plain-text version
        html=render_html(report_md), # formatted version
        category=category,
    )

    client = mt.MailtrapClient(token=api_token)
    return client.send(mail)