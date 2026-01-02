import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp import Context
from core.video_converter import VideoConverter
from core.utils import file_url_to_path
from mcp.types import TextContent # <--- ADDED IMPORT



# Define the absolute path to your ffmpeg executable here.
# Using the junction you created is a great, stable path.
FFMPEG_EXECUTABLE_PATH = r"C:\ffmpeg\ffmpeg.exe"


# Verify it exists on startup to fail fast
if not os.path.exists(FFMPEG_EXECUTABLE_PATH):
    print(f"WARNING: FFmpeg not found at {FFMPEG_EXECUTABLE_PATH}. Video conversion will fail.")
    
mcp = FastMCP("VidsMCP", log_level="ERROR")


async def is_path_allowed(requested_path: Path, ctx: Context) -> bool:
    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    try:
        requested_path = requested_path.resolve(strict=False)
        # --- DEBUG PRINT ---
        print(f"DEBUG: Requested path (resolved): {requested_path}")
        # -------------------
    except Exception as e:
        print(f"Error resolving requested path {requested_path}: {e}")
        return False

    if requested_path.is_file():
        requested_path = requested_path.parent

    for root in client_roots:
        root_path = Path(file_url_to_path(root.uri)).resolve(strict=True)
        # --- DEBUG PRINT ---
        print(f"DEBUG: Checking against root: {root_path}")
        # -------------------
        
        try:
            common = os.path.commonpath([root_path, requested_path])
            # --- DEBUG PRINT ---
            print(f"DEBUG: Common path: {common}")
            # -------------------
            if common == str(root_path):
                 return True
        except ValueError:
            continue

    print(f"Access denied: Path '{requested_path}' is not within allowed roots.")
    return False


@mcp.tool()
async def convert_video(
    input_path: str = Field(description="Input video file (e.g. Test.mp4)"),
    format: str = Field(description="Output format: gif, mov, webm, mkv, avi"),
    *,
    ctx: Context
) -> str:
    """Convert a video file to another format."""
    from pathlib import Path  # ← Add this if not already at top

    input_file = VideoConverter.validate_input(input_path)

    if not await is_path_allowed(input_file, ctx):
        raise ValueError("Access denied: file not in allowed directory")

    try:
        # Run the conversion
        await VideoConverter.convert(
            input_path=input_path,
            format=format,
            ffmpeg_path=FFMPEG_EXECUTABLE_PATH
        )

        # Build the full path of the output file
        output_path = VideoConverter.generate_output_path(input_path, format)
        full_output_path = Path(output_path).resolve()

        # This is what Gemini will say to the user
        return (
            f"Done! Your video has been successfully converted to {format.upper()}!\n\n"
            f"File saved as:\n{full_output_path.name}\n\n"
            f"Full location:\n{full_output_path}"
        )

    except Exception as e:
        raise RuntimeError(f"Conversion failed: {str(e)}")

@mcp.tool()
async def list_roots(ctx: Context):
    """
    List all directories that are accessible to this server.
    These are the root directories where files can be read from or written to.
    """
    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots
    # It's good practice to resolve these too for consistency
    return [str(Path(file_url_to_path(root.uri)).resolve()) for root in client_roots]


@mcp.tool()
async def read_dir(
    path: str = Field(description="Path to a directory to read"),
    *,
    ctx: Context,
):
    """Read directory contents. Path must be within one of the client's roots."""
    requested_path = Path(path)

    if not await is_path_allowed(requested_path, ctx):
        raise ValueError("Error: can only read directories within a root")
    
    # Re-resolve for iterdir after it passed the check
    requested_path = requested_path.resolve()
    return [entry.name for entry in requested_path.iterdir()]


if __name__ == "__main__":
    mcp.run(transport="stdio")
















# import os
# from pathlib import Path
# from mcp.server.fastmcp import FastMCP
# from pydantic import Field
# from mcp.server.fastmcp import Context
# from core.video_converter import VideoConverter
# from core.utils import file_url_to_path



# # Define the absolute path to your ffmpeg executable here.
# # Using the junction you created is a great, stable path.
# FFMPEG_EXECUTABLE_PATH = r"C:\ffmpeg\ffmpeg.exe"


# # Verify it exists on startup to fail fast
# if not os.path.exists(FFMPEG_EXECUTABLE_PATH):
#     print(f"WARNING: FFmpeg not found at {FFMPEG_EXECUTABLE_PATH}. Video conversion will fail.")
    
# mcp = FastMCP("VidsMCP", log_level="ERROR")


# async def is_path_allowed(requested_path: Path, ctx: Context) -> bool:
#     roots_result = await ctx.session.list_roots()
#     client_roots = roots_result.roots

#     try:
#         requested_path = requested_path.resolve(strict=False)
#         # --- DEBUG PRINT ---
#         print(f"DEBUG: Requested path (resolved): {requested_path}")
#         # -------------------
#     except Exception as e:
#         print(f"Error resolving requested path {requested_path}: {e}")
#         return False

#     if requested_path.is_file():
#         requested_path = requested_path.parent

#     for root in client_roots:
#         root_path = Path(file_url_to_path(root.uri)).resolve(strict=True)
#         # --- DEBUG PRINT ---
#         print(f"DEBUG: Checking against root: {root_path}")
#         # -------------------
        
#         try:
#             common = os.path.commonpath([root_path, requested_path])
#             # --- DEBUG PRINT ---
#             print(f"DEBUG: Common path: {common}")
#             # -------------------
#             if common == str(root_path):
#                  return True
#         except ValueError:
#             continue

#     print(f"Access denied: Path '{requested_path}' is not within allowed roots.")
#     return False


# @mcp.tool()
# async def convert_video(
#     input_path: str = Field(description="Path to the input MP4 file"),
#     format: str = Field(description="Output format (e.g. 'mov')"),
#     *,
#     ctx: Context,
# ):
#     """Convert an MP4 video file to another format using ffmpeg"""
#     # validate_input returns a Path object
#     input_file = VideoConverter.validate_input(input_path)

#     # Ensure the input file is contained in a root
#     if not await is_path_allowed(input_file, ctx):
#         # Log the exact paths being compared for debugging
#         roots_result = await ctx.session.list_roots()
#         client_roots = [str(Path(file_url_to_path(r.uri)).resolve()) for r in roots_result.roots]
#         print(f"DEBUG: Access denied. Requested: {input_file.resolve()}, Roots: {client_roots}")
#         raise ValueError(f"Access to path is not allowed: {input_path}")

#     return await VideoConverter.convert(input_path, format, ffmpeg_path=FFMPEG_EXECUTABLE_PATH)


# @mcp.tool()
# async def list_roots(ctx: Context):
#     """
#     List all directories that are accessible to this server.
#     These are the root directories where files can be read from or written to.
#     """
#     roots_result = await ctx.session.list_roots()
#     client_roots = roots_result.roots
#     # It's good practice to resolve these too for consistency
#     return [str(Path(file_url_to_path(root.uri)).resolve()) for root in client_roots]


# @mcp.tool()
# async def read_dir(
#     path: str = Field(description="Path to a directory to read"),
#     *,
#     ctx: Context,
# ):
#     """Read directory contents. Path must be within one of the client's roots."""
#     requested_path = Path(path)

#     if not await is_path_allowed(requested_path, ctx):
#         raise ValueError("Error: can only read directories within a root")
    
#     # Re-resolve for iterdir after it passed the check
#     requested_path = requested_path.resolve()
#     return [entry.name for entry in requested_path.iterdir()]


# if __name__ == "__main__":
#     mcp.run(transport="stdio")