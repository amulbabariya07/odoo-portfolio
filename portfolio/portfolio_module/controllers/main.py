from odoo import http
from odoo.http import request

def extract_id_from_slug(slug_str):
    try:
        return int(slug_str)
    except ValueError:
        pass
    try:
        return int(slug_str.split('-')[-1])
    except (ValueError, IndexError, AttributeError):
        return False

class PortfolioModuleController(http.Controller):

    @http.route(['/my-module', '/my-modules', '/my-modules/page/<int:page>'], type='http', auth="public", website=True)
    def my_modules(self, page=1, search='', tag='', **kw):
        domain = []
        if search:
            domain += ['|', ('name', 'ilike', search), ('short_description', 'ilike', search)]
        
        tag_id = False
        if tag:
            try:
                tag_id = int(tag)
                domain += [('tag_ids', 'in', [tag_id])]
            except ValueError:
                pass
                
        versions = request.httprequest.args.getlist('versions')
        if versions:
            domain += [('version', 'in', versions)]
            
        ir_module_ids_str = request.httprequest.args.getlist('ir_module_ids')
        ir_module_ids = []
        for mod_id in ir_module_ids_str:
            try:
                ir_module_ids.append(int(mod_id))
            except ValueError:
                pass
        if ir_module_ids:
            domain += [('module_ids', 'in', ir_module_ids)]
                
        url = '/my-modules'
        total = request.env['portfolio.module'].sudo().search_count(domain)
        
        url_args = {'search': search, 'tag': tag}
        if versions:
            url_args['versions'] = versions
        if ir_module_ids:
            url_args['ir_module_ids'] = ir_module_ids
            
        pager = request.website.pager(url=url, total=total, page=page, step=12, url_args=url_args)
        
        modules = request.env['portfolio.module'].sudo().search(domain, limit=12, offset=pager['offset'])
        tags = request.env['portfolio.module.tag'].sudo().search([])
        
        # Get used versions and used modules
        all_modules = request.env['portfolio.module'].sudo().search([])
        used_versions = sorted(list(set(m.version for m in all_modules if m.version)), reverse=True)
        used_ir_modules = all_modules.mapped('module_ids')
        
        return request.render('portfolio_module.index', {
            'modules': modules,
            'pager': pager,
            'search': search,
            'current_tag': tag_id,
            'current_versions': versions,
            'current_ir_module_ids': ir_module_ids,
            'all_tags': tags,
            'used_versions': used_versions,
            'used_ir_modules': used_ir_modules,
        })

    @http.route(['/my-module/<string:slug_str>', '/my-modules/<string:slug_str>'], type='http', auth="public", website=True)
    def module_detail(self, slug_str, **kw):
        module_id = extract_id_from_slug(slug_str)
        if not module_id:
            return request.not_found()
        module = request.env['portfolio.module'].sudo().browse(module_id)
        if not module.exists():
            return request.not_found()
        return request.render('portfolio_module.detail', {
            'module': module,
        })
