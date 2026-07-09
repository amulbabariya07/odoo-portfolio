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

    @http.route('/portfolio/contact/action/<int:contact_id>/<string:action_type>', type='http', auth="public", website=True)
    def contact_email_action(self, contact_id, action_type, token=None, **kw):
        if not token:
            return "Missing security token. Action forbidden."

        # Check if record exists at all
        contact_exists = request.env['portfolio.contact'].sudo().search([('id', '=', contact_id)], limit=1)
        
        if not contact_exists:
            error_msg = "This query has already been deleted or no longer exists."
            return request.make_response(f"""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f1f5f9;">
                    <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                        <h2 style="color: #ef4444; margin-top: 0;">Link Expired</h2>
                        <p style="font-size: 16px; color: #334155;">{error_msg}</p>
                    </div>
                </body>
            </html>
            """)

        contact = request.env['portfolio.contact'].sudo().search([
            ('id', '=', contact_id),
            ('access_token', '=', token)
        ], limit=1)

        if not contact:
            error_msg = "This action has already been performed. Link is now expired (Access Denied)."
            return request.make_response(f"""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f1f5f9;">
                    <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                        <h2 style="color: #ef4444; margin-top: 0;">Access Denied</h2>
                        <p style="font-size: 16px; color: #334155;">{error_msg}</p>
                    </div>
                </body>
            </html>
            """)

        if action_type == 'progress':
            contact.state = 'in_progress'
            # Invalidate token so it can't be used again
            contact.access_token = False
            message = "Query marked as In Progress."
        elif action_type == 'delete':
            contact.unlink()
            message = "Query successfully deleted."
        else:
            return "Invalid action type."

        return request.make_response(f"""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f1f5f9;">
                    <div style="max-width: 500px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
                        <h2 style="color: #0ea5e9; margin-top: 0;">Success</h2>
                        <p style="font-size: 16px; color: #334155;">{message}</p>
                        <p style="font-size: 14px; margin-top: 30px; color: #94a3b8;">You can now safely close this window.</p>
                    </div>
                </body>
            </html>
        """)
