from models import Product
from extensions import db
from app import app
from sqlalchemy.exc import SQLAlchemyError

def add_product_to_db():
    with app.app_context(): 
        product_name = "Gorilla® Universal HEvans® Plate"
        existing_product = Product.query.filter_by(product_name=product_name).first()

        if existing_product:
            print(f"Product {product_name} already exists in the database.")
            return

        product = Product()
        product.product_name = product_name
        product.slug = product_name.lower().replace(" ", "-")

        product.product_info = """The Gorilla® HEvans® plate was designed for use with the Evans Calcaneal Osteotomy. The plate uses a 3 screw fixation construct to support the graft placed into the osteotomy and helps to prevent graft subsidence with subsequent loss of calcaneal length seen in the early post-operative period due to graft resorption.
        The design allows for a single proximal screw to be placed in the calcaneus with two distal screws placed in the anterior fragment of the calcaneus. Dual point fixation at the distal fragment mitigates the prospect of rotation of the distal fragment with the calcaneocuboid anatomy. The posterior aspect of the plate is tapered to prevent peroneal tendon irritation in the location of the plate.
        The HEvans® plate is low profile (1.1 mm), with a tapering of the thickness to 0.5 mm toward the end to prevent soft tissue irritation."""

        product.design_rationale = """Paragon 28®’s Design Rationale: Why a 3 hole plate? Paragon 28® chose to design a 3 hole plate option for the Evans Calcaneal Osteotomy procedure to allow for less potential for soft tissue irritation at the posterior aspect, where interference with the peroneal tendons and/or sural nerve is a risk. 
        The 3 hole HEvans® plate provides rotational stability for this procedure because of the large, flat calcaneocuboid joint. 
        Because rotation about the proximal hole would require an arched path of the distal fragment, this is blocked by the calcaneocuboid joint."""

        try:
            db.session.add(product)
            db.session.commit()
            print(f"Product {product_name} has been added to the database.")
        except SQLAlchemyError as e:
            print(f"An error occurred while adding {product_name} to the database: {e}")

add_product_to_db()