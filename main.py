import logging
import pylib.cad_prompts
import pylib.speech_to_text
from pylib.openai_text import generate_ai_text
from pylib.modeling import text_to_cad, check_model_generation_status
from pylib.slice_print import slice_with_prusaslicer, send_gcode_to_printer, find_latest_stl  # Assuming you have a function for AI text generation

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
USE_SPEECH = True  # Set this to False to type your idea instead
USE_AI_FOR_IDEA = False  # Set this to True to let AI generate the idea
STL_BASE_DIR = "your-path-to-AlmechE"  # Update with your path

# Main function
def main():
    try:
        # Idea generation or input
        if USE_SPEECH and not USE_AI_FOR_IDEA:
            logging.info("Please speak your idea for a CAD object:")
            idea = input("Give me your idea, bitch: ")
            # idea = pylib.speech_to_text.recognize_speech()
        elif USE_AI_FOR_IDEA:
            logging.info("Generating idea using AI...")
            idea = generate_ai_text(pylib.cad_prompts.IDEA_GENERATION, 0.8)  # Adjust temperature as needed
        else:
            idea = input("Please type your idea for a CAD object: ")

        logging.info(f"Idea received: {idea}")

        # Generate manufacturing instructions
        instructions_prompt = pylib.cad_prompts.MANUFACTURING_INSTRUCTIONS.format(user_idea=idea)
        manufacturing_instructions = generate_ai_text(instructions_prompt, 0.8)
        logging.info(f"Manufacturing Instructions:\n{manufacturing_instructions}")

        # Generate the CAD model using the final instructions
        operation_id = text_to_cad(manufacturing_instructions, "stl")
        if operation_id:
            logging.info(f"CAD model generation initiated. Operation ID: {operation_id}")
            while True:
                result = check_model_generation_status(operation_id)
                if result and result.get("status") == "completed":
                    logging.info("Model generation completed successfully.")
                    stl_path = find_latest_stl(STL_BASE_DIR)
                    slice_with_prusaslicer(stl_path)  # Slicing the STL
                    send_gcode_to_printer()  # Sending to printer
                    break
                elif result and result.get("status") == "failed":
                    logging.error("Model generation failed.")
                    break

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
