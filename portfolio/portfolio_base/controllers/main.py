from odoo import http
from odoo.http import request

class PortfolioController(http.Controller):

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        profile = request.env['portfolio.profile'].sudo().search([], limit=1)
        return request.render('portfolio_base.portfolio_home_page', {
            'profile': profile,
            'main_object': profile,
            'submitted': kw.get('submitted', False),
        })

    @http.route('/contact', type='http', auth="public", website=True)
    def contact(self, **kw):
        profile = request.env['portfolio.profile'].sudo().search([], limit=1)
        return request.render('portfolio_base.portfolio_contact_page', {
            'profile': profile,
            'submitted': kw.get('submitted', False),
        })

    @http.route('/contact/submit', type='http', auth="public", methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **kw):
        print("======== CONTACT SUBMIT REACHED ========")
        print("FORM DATA RECEIVED:", kw)
        
        redirect_url = kw.get('redirect_url', '/contact?submitted=1')
        error_url = kw.get('redirect_url', '/contact').replace('?submitted=1', '').replace('submitted=1', '')

        if not kw.get('name') or not kw.get('description') or (not kw.get('email') and not kw.get('phone')):
            print("ERROR: Required fields missing!")
            return request.redirect(error_url)

        try:
            attachments = request.httprequest.files.getlist('attachment')
            attachment_commands = []
            import base64
            for att in attachments:
                if att and hasattr(att, 'read'):
                    filename = att.filename
                    if filename:
                        attachment_commands.append((0, 0, {
                            'name': filename,
                            'type': 'binary',
                            'datas': base64.b64encode(att.read()),
                        }))

            print("CREATING RECORD...")
            record = request.env['portfolio.contact'].sudo().create({
                'name': kw.get('name'),
                'email': kw.get('email'),
                'phone': kw.get('phone'),
                'description': kw.get('description'),
                'attachment_ids': attachment_commands,
            })
            print("RECORD CREATED SUCCESSFULLY! ID:", record.id)

            return request.redirect(redirect_url)
        except Exception as e:
            print("EXCEPTION OCCURRED DURING CREATION:", str(e))
            return request.redirect(error_url)
