from models import Product
from extensions import db
from app import app
from sqlalchemy.exc import SQLAlchemyError

def add_products_to_db(products):
    with app.app_context(): 
        for product_info in products:
            product_name = product_info['product_name']
            existing_product = Product.query.filter_by(product_name=product_name).first()

            if existing_product:
                print(f"Product {product_name} already exists in the database.")
                continue

            product = Product()
            product.product_name = product_name
            product.slug = product_name.lower().replace(" ", "-")
            product.product_info = product_info['product_info']
            product.design_rationale = product_info.get('design_rationale')

            try:
                db.session.add(product)
                db.session.commit()
                print(f"Product {product_name} has been added to the database.")
            except SQLAlchemyError as e:
                print(f"An error occurred while adding {product_name} to the database: {e}")

products = [
    {
        'product_name': "Gorilla® Universal HEvans® Plate",
        'product_info': """The Gorilla® HEvans® plate was designed for use with the Evans Calcaneal Osteotomy. The plate uses a 3 screw fixation construct to support the graft placed into the osteotomy and helps to prevent graft subsidence with subsequent loss of calcaneal length seen in the early post-operative period due to graft resorption.
        The design allows for a single proximal screw to be placed in the calcaneus with two distal screws placed in the anterior fragment of the calcaneus. Dual point fixation at the distal fragment mitigates the prospect of rotation of the distal fragment with the calcaneocuboid anatomy. The posterior aspect of the plate is tapered to prevent peroneal tendon irritation in the location of the plate.
        The HEvans® plate is low profile (1.1 mm), with a tapering of the thickness to 0.5 mm toward the end to prevent soft tissue irritation.""",
        'design_rationale': """Paragon 28®’s Design Rationale: Why a 3 hole plate? Paragon 28® chose to design a 3 hole plate option for the Evans Calcaneal Osteotomy procedure to allow for less potential for soft tissue irritation at the posterior aspect, where interference with the peroneal tendons and/or sural nerve is a risk. 
        The 3 hole HEvans® plate provides rotational stability for this procedure because of the large, flat calcaneocuboid joint. Because rotation about the proximal hole would require an arched path of the distal fragment, this is blocked by the calcaneocuboid joint."""
    },

    {
        'product_name': "Gorilla® Lapidus Arthrodesis System",
        'product_info': """The Gorilla® Lapidus Arthrodesis System development began around the concept of neutralization plating. A plate designed for the medial wall provides added stiffness since the plate is positioned on its side. Traditionally, medial wall plates add a complicating factor in that the distal screws apply adductory force on the 1st metatarsal as they are tightened to the plate. To combat this, Paragon 28® designed the plates to match the corrected metatarsal position as well as curvature, thus following the principles of a “bent plate technique” to limit the adductory force applied to the metatarsal. In addition, a medial wall plate is better positioned to prevent plantar gapping while avoiding the insertion of the tibialis anterior plantarly. The anatomic plate construct is designed to help reduce soft tissue irritation in an area where ample soft tissue coverage can be a concern with a poorly designed plate construct.
        These features were incorporated into all 18 Lapidus Arthrodesis plating options: standard, graft-spanning and medial wall step-off.
        A Precision® Guide Lapidus screw guide is provided in the system to allow for placement of a lag screw across the Lapidus Arthrodesis while missing all other screws in the construct."""
        'design_rationale': """Paragon 28® captured the essence of surgeon concerns with the Lapidus procedure by addressing them with several patented features: a medially positioned plate, a ramped plate proximally to avoid tendon irritation, anatomic curvature of the plate to provide a bent plate advantage, a plantar locking arm to better resist the tension side of the joint, and a Precision® Guide Lapidus for crossing screw insertion to avoid collision with the locking plate screws."""
    },

    {
        'product_name': "Lapidus Cut Guide System",
        'product_info': """The Lapidus Cut Guide System was created to provide a reproducible and streamlined means to achieve calculated bi-planar correction with transverse cuts, or tri-planar correction with the surgeons preferred method of de-rotation. 
        The system allows for controlled cuts that minimize the amount of length lost on the first ray by offering users an array of cut guides to resect the precise amount of bone from the first TMT joint in order to restore the desired IM angle."""
    },

    


]

add_products_to_db(products)
