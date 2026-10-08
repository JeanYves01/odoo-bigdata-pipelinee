"""Add usable filters to the 32 saved Odoo Metabase SQL questions and map them
onto the four existing dashboards. Default mode is a read-only server-resolved plan.
Run with --apply only after reviewing the plan output.
"""
from __future__ import annotations
import argparse, getpass, json, sys, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=__import__('os').environ.get('METABASE_URL','http://localhost:3000').rstrip('/')
SQL_DIR=ROOT/'metabase'/'interactive_sql'
COLLECTION='Odoo Analytics'

# Exact saved-question titles from the prior bulk creation.
CARDS={
'Ventes':{
'CA total':'ventes/01_ca_total.sql','Marge brute':'ventes/02_marge_brute.sql','Nombre de commandes':'ventes/03_nb_commandes.sql','Panier moyen':'ventes/04_panier_moyen.sql','CA mensuel':'ventes/05_ca_mensuel.sql','Top 10 clients':'ventes/06_top10_clients.sql','CA par catégorie':'ventes/07_ca_par_categorie.sql','Marge mensuelle':'ventes/08_marge_mensuelle.sql'},
'Production':{
'Couverture TRS mesuré':'production/01_couverture_trs.sql','TRS moyen (non mesurable)':'production/02_trs_moyen_non_disponible.sql','Ordres réalisés vs total':'production/03_ordres_realises_vs_total.sql','Durée moyenne des ordres terminés':'production/04_duree_moyenne_heures.sql','Quantité produite par mois':'production/05_qte_produite_mensuelle.sql','Production par produit':'production/06_production_par_produit.sql','Ordres par statut':'production/07_ordres_par_statut.sql','Durée moyenne par mois':'production/08_duree_mensuelle.sql'},
'Achats':{
'Montant total des achats':'achats/01_montant_total.sql','Couverture des délais mesurés':'achats/02_couverture_delai_livraison.sql','Couverture de conformité mesurée':'achats/03_couverture_conformite.sql','Top 10 fournisseurs':'achats/04_top10_fournisseurs.sql','Achats par mois':'achats/05_montant_mensuel.sql','Achats par catégorie':'achats/06_montant_par_categorie.sql','Commandes par statut':'achats/07_commandes_par_statut.sql','Quantité par fournisseur':'achats/08_quantite_par_fournisseur.sql'},
'Stocks':{
'Valeur de stock estimée':'stocks/01_valeur_stock_estimee.sql','Rotation estimée (proxy)':'stocks/02_rotation_estimee.sql','Produits au solde négatif':'stocks/03_produits_solde_negatif.sql','Stock par entrepôt':'stocks/04_stock_par_entrepot.sql','Mouvements : entrées et sorties':'stocks/05_mouvements_entrees_sorties.sql','Top 10 valeur de stock':'stocks/06_top10_valeur_stock.sql','Solde estimé par produit':'stocks/07_solde_par_produit.sql','Mouvements par mois':'stocks/08_mouvements_mensuels.sql'}}

FILTERS={
'Ventes':['date_from','date_to','product','category','client'],
'Production':['date_from','date_to','product','category','status'],
'Achats':['date_from','date_to','product','category','supplier'],
'Stocks':['date_from','date_to','product','category','warehouse']}
LABELS={'date_from':'Date de début','date_to':'Date de fin','product':'Produit (contient)','category':'Catégorie (contient)','client':'Client (contient)','supplier':'Fournisseur (contient)','status':'Statut (contient)','warehouse':'Entrepôt (contient)'}
FTYPES={'date_from':'date','date_to':'date','product':'text','category':'text','client':'text','supplier':'text','status':'text','warehouse':'text'}
PTYPES={'date_from':'date/single','date_to':'date/single','product':'text','category':'text','client':'text','supplier':'text','status':'text','warehouse':'text'}

def req(path, method='GET', data=None, token=None):
    raw=None if data is None else json.dumps(data,ensure_ascii=False).encode()
    h={'Accept':'application/json'}
    if raw is not None:h['Content-Type']='application/json'
    if token:h['X-Metabase-Session']=token
    r=urllib.request.Request(BASE+path,data=raw,headers=h,method=method)
    try:
        with urllib.request.urlopen(r,timeout=60) as x:
            b=x.read(); return json.loads(b.decode()) if b else None
    except urllib.error.HTTPError as e: raise RuntimeError(f'{method} {path}: HTTP {e.code} {e.read().decode("utf-8", "replace")}') from e

def listing(x):
    if isinstance(x,list):return x
    if isinstance(x,dict):
        for k in ('data','results','items'):
            if isinstance(x.get(k),list):return x[k]
    return []

def find_cards(token):
    found={}
    for dashboard, cards in CARDS.items():
        for name in cards:
            q=urllib.parse.urlencode({'query':name,'models':'card','limit':50})
            hits=listing(req('/api/search?'+q,token=token))
            item=next((r for r in hits if r.get('name','').casefold()==name.casefold() and r.get('model')=='card'),None)
            if not item:
                # Some Metabase versions omit model on search results.
                item=next((r for r in hits if r.get('name','').casefold()==name.casefold()),None)
            if item: found[(dashboard,name)]=item
    return found

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--apply',action='store_true'); args=ap.parse_args()
    username=input('Identifiant/e-mail Metabase : ').strip(); password=getpass.getpass('Mot de passe Metabase : ')
    sess=req('/api/session','POST',{'username':username,'password':password}); token=sess.get('id')
    if not token: raise RuntimeError('Session Metabase invalide.')
    try:
        dbs=listing(req('/api/database',token=token)); db=next((d for d in dbs if d.get('name','').casefold()=='odoo analytics'),None)
        if not db: raise RuntimeError("Base Metabase 'Odoo Analytics' introuvable.")
        existing=find_cards(token)
        dashboard_list=listing(req('/api/dashboard',token=token))
        existing_dashboards={name:next((d for d in dashboard_list if d.get('name','').casefold()==name.casefold()),None) for name in CARDS}
        expected=sum(len(x) for x in CARDS.values())
        print(f'PLAN: {expected} questions à mettre à jour, 4 dashboards à relier, base={db["name"]}.')
        print('Échantillon des questions: '+', '.join(list(CARDS['Ventes'])[:4])+'.')
        print('Filtres: période début/fin, produit et catégorie; client (ventes), fournisseur (achats), statut (production), entrepôt (stocks).')
        missing=[name for group in CARDS.values() for name in group if not any(k[1]==name for k in existing)]
        missing_dashboards=[name for name,item in existing_dashboards.items() if not item]
        if missing: raise RuntimeError(f'{len(missing)} questions manquent ou ne sont pas retrouvées; aucun changement appliqué. Exemples: {missing[:5]}')
        if missing_dashboards: raise RuntimeError(f'Dashboards manquants: {missing_dashboards}; aucun changement appliqué.')
        print('Résolution Metabase: les 32 questions et les 4 dashboards attendus sont trouvés.')
        if not args.apply:
            print('AUCUNE MODIFICATION effectuée. Après validation, relancer avec --apply.')
            return
        # Update saved cards with SQL and optional Metabase template tags.
        cardids={}
        for dashboard, group in CARDS.items():
            for name, rel in group.items():
                hit=existing[(dashboard,name)]; card_id=hit['id']; card=req(f'/api/card/{card_id}',token=token)
                sql=(SQL_DIR/rel).read_text(encoding='utf-8-sig').strip().rstrip(';')+';'
                tags={}; pars=[]
                for key in FILTERS[dashboard]:
                    # Non-measurable cards have no filter hooks by design.
                    if name in ('TRS moyen (non mesurable)','Couverture de conformité mesurée'):
                        continue
                    typ=FTYPES[key]; tagid=str(uuid.uuid5(uuid.NAMESPACE_URL,f'odoo-analytics:{dashboard}:{name}:{key}'))
                    tags[key]={'id':tagid,'name':key,'display-name':LABELS[key],'type':typ,'required':False,'default':None}
                    if typ=='date': tags[key]['widget-type']='date/single'
                    # Basic text variables use widget type 'text'; contains semantics
                    # are implemented by the SQL positionCaseInsensitiveUTF8 predicate.
                    else: tags[key]['widget-type']='text'
                    pars.append({'id':key,'name':LABELS[key],'slug':key,'type':PTYPES[key],'target':['variable',['template-tag',key]]})
                # Rebuild a clean legacy native dataset_query. GET /api/card may return
                # MBQL 5/lib serialization; mixing its lib/type structure with legacy
                # native keys causes HTTP 400 on PUT in current Metabase releases.
                dsq={'database':db['id'],'type':'native',
                     'native':{'query':sql,'template-tags':tags}}
                payload={'name':card['name'],'description':card.get('description'),'collection_id':card.get('collection_id'),
                         'dataset_query':dsq,'display':card.get('display','table'),
                         'visualization_settings':card.get('visualization_settings') or {},
                         'parameters':pars,'type':card.get('type','question')}
                req(f'/api/card/{card_id}','PUT',payload,token)
                cardids[(dashboard,name)]=card_id
                print(f'  Mis à jour: {name}')
        # Update four dashboard filters and mappings. Preserve card positions and unrelated settings.
        for dashboard, group in CARDS.items():
            hits=listing(req('/api/dashboard',token=token)); item=next((d for d in hits if d.get('name','').casefold()==dashboard.casefold()),None)
            if not item: raise RuntimeError(f'Dashboard manquant: {dashboard}; cartes mises à jour, dashboards non finalisés.')
            detail=req(f'/api/dashboard/{item["id"]}',token=token)
            old=detail.get('dashcards') or detail.get('ordered_cards') or []
            bycard={d.get('card_id') or (d.get('card') or {}).get('id'):d for d in old}
            params=[]
            for key in FILTERS[dashboard]:
                params.append({'id':key,'name':LABELS[key],'slug':key,'type':PTYPES[key],
                               'sectionId':'date' if key.startswith('date_') else 'string','default':None,
                               'target':['variable',['template-tag',key]]})
            dashcards=[]; row=0; col=0
            for name in group:
                cid=cardids[(dashboard,name)]; olddc=bycard.get(cid)
                if olddc:
                    dcid=olddc.get('id',-1-len(dashcards)); r=olddc.get('row',0); c=olddc.get('col',0); sx=olddc.get('size_x',6); sy=olddc.get('size_y',4)
                    mappings=list(olddc.get('parameter_mappings') or [])
                else:
                    dcid=-1-len(dashcards); r=row; c=col; sx=6; sy=4; mappings=[]
                available=FILTERS[dashboard]
                if name in ('TRS moyen (non mesurable)','Couverture de conformité mesurée'):
                    available=[]
                for key in available:
                    mp={'card_id':cid,'parameter_id':key,'target':['variable',['template-tag',key]]}
                    if not any(x.get('parameter_id')==key for x in mappings): mappings.append(mp)
                dashcards.append({'id':dcid,'card_id':cid,'row':r,'col':c,'size_x':sx,'size_y':sy,
                                  'parameter_mappings':mappings,'series':olddc.get('series',[]) if olddc else [],
                                  'visualization_settings':olddc.get('visualization_settings') or {} if olddc else {},
                                  'inline_parameters':olddc.get('inline_parameters') or [] if olddc else []})
                col+=6
                if col>=12:col=0;row+=4
            req(f'/api/dashboard/{item["id"]}','PUT',{'parameters':params,'dashcards':dashcards},token)
            print(f'  Filtres reliés: {dashboard}')
        print('TERMINÉ: questions mises à jour et filtres reliés. Ouvre chaque dashboard et teste période + filtre texte.')
    finally:
        try:req('/api/session','DELETE',{},token)
        except Exception:pass
if __name__=='__main__':
    try:main()
    except Exception as e:print('ERREUR:',e,file=sys.stderr);sys.exit(1)
