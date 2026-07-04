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
            attachment = kw.get('attachment')
            attachment_data = False
            attachment_name = ''
            if attachment and hasattr(attachment, 'read'):
                import base64
                attachment_data = base64.b64encode(attachment.read())
                attachment_name = attachment.filename

            print("CREATING RECORD...")
            record = request.env['portfolio.contact'].sudo().create({
                'name': kw.get('name'),
                'email': kw.get('email'),
                'phone': kw.get('phone'),
                'description': kw.get('description'),
                'attachment': attachment_data,
                'attachment_name': attachment_name,
            })
            print("RECORD CREATED SUCCESSFULLY! ID:", record.id)
            return request.redirect(redirect_url)
        except Exception as e:
            print("EXCEPTION OCCURRED DURING CREATION:", str(e))
            return request.redirect(error_url)
